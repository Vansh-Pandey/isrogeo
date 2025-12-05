 
from PIL import Image
from typing import Union, List, Tuple, Optional, Dict
import os
import traceback
import torch
import json
import re
import numpy as np
import cv2
from pathlib import Path


class GroundingService:
    
    def __init__(
        self,
        yolo_model_path: str = "training_output/vrsbench_v2_obb2/weights/best.pt",
        geoground_model_path: str = "geo_kabir/GeoGround/llava-v1.5-7b-task-geoground",
        device: str = None,
        yolo_conf_threshold: float = 0.4,
        selection_threshold: float = 0.6,
        config: dict = None
    ):
         
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.yolo_model_path = yolo_model_path
        self.geoground_model_path = geoground_model_path
        self.yolo_conf_threshold = yolo_conf_threshold
        self.selection_threshold = selection_threshold
        self.config = config or {}

        print("=" * 80)
        print("🚀 HYBRID GROUNDING SERVICE - INITIALIZATION")
        print("=" * 80)
        print(f"Device: {self.device}")
        print(f"YOLO Model: {yolo_model_path}")
        print(f"GeoGround Model: {geoground_model_path}")
        print(f"YOLO Confidence: {yolo_conf_threshold}")
        print(f"Selection Threshold: {selection_threshold}")
        print("⚠️  OBB FORMAT: 8-point normalized (x1,y1,x2,y2,x3,y3,x4,y4)")
        print("=" * 80)

        self.total_queries = 0
        self.yolo_selections = 0
        self.geoground_selections = 0
        self.failed_queries = 0
        self.total_detections = 0

        self.yolo_model = None
        self.geoground_model = None
        self.tokenizer = None
        self.image_processor = None
        self.conv_mode = self.config.get('conv_mode', 'llava_v1')

        self._load_yolo_model()
        self._load_geoground_model()

        print("✅ Hybrid Grounding Service initialized successfully!\n")

    def _load_yolo_model(self): 
        try:
            print(f"📦 Loading YOLO model from {self.yolo_model_path}...")
            
            from ultralytics import YOLO
            
            if not os.path.exists(self.yolo_model_path):
                print(f"⚠️  YOLO model not found at {self.yolo_model_path}")
                print("   Will fall back to GeoGround for all queries")
                self.yolo_model = None
                return
            
            self.yolo_model = YOLO(self.yolo_model_path)
            self.yolo_model.to(self.device)
            
            print(f"✅ YOLO model loaded successfully")
            
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            traceback.print_exc()
            self.yolo_model = None

    def _load_geoground_model(self): 
        try:
            print(f"📦 Loading GeoGround model from {self.geoground_model_path}...")
            
            from llava.model.builder import load_pretrained_model
            from llava.mm_utils import get_model_name_from_path, tokenizer_image_token
            from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
            from llava.conversation import conv_templates

            self.IMAGE_TOKEN_INDEX = IMAGE_TOKEN_INDEX
            self.DEFAULT_IMAGE_TOKEN = DEFAULT_IMAGE_TOKEN
            self.tokenizer_image_token = tokenizer_image_token
            self.conv_templates = conv_templates

            if not os.path.exists(self.geoground_model_path):
                print(f"⚠️  GeoGround model not found at {self.geoground_model_path}")
                print("   Will use YOLO for all queries")
                self.geoground_model = None
                return

            model_name = get_model_name_from_path(self.geoground_model_path)

            self.tokenizer, self.geoground_model, self.image_processor, context_len = load_pretrained_model(
                model_path=self.geoground_model_path,
                model_base=None,
                model_name=model_name,
                device=self.device,
                load_8bit=False,
                load_4bit=False
            )

            self._apply_geoground_fixes()

            print(f"✅ GeoGround model loaded: {model_name}")
            print(f"   Context length: {context_len}")
            print(f"   Conversation mode: {self.conv_mode}")

        except Exception as e:
            print(f"❌ Failed to load GeoGround model: {e}")
            traceback.print_exc()
            self.geoground_model = None

    def _apply_geoground_fixes(self): 
        try:
            print("🔧 Applying GeoGround compatibility fixes...")
             
            target_dtype = torch.float16 if self.device == "cuda" else torch.float32
 
            self.geoground_model = self.geoground_model.to(device=self.device)
             
            base_model = self.geoground_model.model if hasattr(self.geoground_model, 'model') else self.geoground_model
            
            if hasattr(base_model, 'vision_tower'):
                vt = base_model.vision_tower
                if hasattr(vt, 'vision_tower'):
                    vt.vision_tower = vt.vision_tower.to(dtype=target_dtype)
                else:
                    base_model.vision_tower = vt.to(dtype=target_dtype)
                print(f"  ✅ Vision tower → {target_dtype}")

            if hasattr(base_model, 'mm_projector'):
                base_model.mm_projector = base_model.mm_projector.to(dtype=target_dtype)
                print(f"  ✅ MM projector → {target_dtype}")

            print("✅ GeoGround fixes applied successfully")

        except Exception as e:
            print(f"⚠️  GeoGround fixes warning: {e}")
    def detect_objects(
        self,
        image: Union[str, Image.Image],
        query: str,
        force_model: Optional[str] = None,
        return_metadata: bool = False
    ) -> Union[List[Tuple[str, List[float]]], Tuple[List[Tuple[str, List[float]]], Dict]]:
         
        try:
            self.total_queries += 1
            
            print("\n" + "=" * 80)
            print(f"🔍 QUERY #{self.total_queries}: '{query[:60]}...'")
            print("=" * 80)

            # Load image
            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image not found: {image}")
                image_path = image
                image = Image.open(image)
            else:
                image_path = "memory"

            if not isinstance(image, Image.Image):
                raise ValueError(f"Image must be PIL Image or path, got {type(image)}")

            if image.mode != 'RGB':
                image = image.convert('RGB')

            width, height = image.size
            print(f"📐 Image: {width}x{height} ({image_path})")

            # Model selection logic
            selected_model = None
            yolo_confidence = 0.0
            detections = []
            
            if force_model:
                selected_model = force_model.lower()
                print(f"🎯 Forced model: {selected_model.upper()}")
            else:
                # Try YOLO first for quick detection
                if self.yolo_model is not None:
                    yolo_detections, yolo_confidence = self._run_yolo_inference(image, query)
                    
                    if yolo_confidence >= self.selection_threshold:
                        selected_model = 'yolo'
                        detections = yolo_detections
                        print(f"✅ YOLO selected (confidence: {yolo_confidence:.3f} >= {self.selection_threshold})")
                    else:
                        print(f"⚠️  YOLO confidence too low ({yolo_confidence:.3f} < {self.selection_threshold})")
                
                # Fall back to GeoGround if YOLO didn't meet threshold
                if selected_model is None:
                    if self.geoground_model is not None:
                        selected_model = 'geoground'
                        print(f"🔄 Falling back to GeoGround")
                    elif self.yolo_model is not None:
                        # Use YOLO anyway if GeoGround not available
                        selected_model = 'yolo'
                        detections = yolo_detections
                        print(f"⚠️  Using YOLO (GeoGround not available)")

            # Run appropriate model
            if selected_model == 'yolo' and not detections:
                if self.yolo_model is not None:
                    detections, yolo_confidence = self._run_yolo_inference(image, query)
                    self.yolo_selections += 1
                else:
                    print("❌ YOLO model not available")
                    detections = []
                    
            elif selected_model == 'geoground':
                if self.geoground_model is not None:
                    detections = self._run_geoground_inference(image, query)
                    self.geoground_selections += 1
                else:
                    print("❌ GeoGround model not available")
                    detections = []

            self.total_detections += len(detections)
            
            print(f"\n✅ Detected {len(detections)} objects using {selected_model.upper()}")
            print("=" * 80)

            if return_metadata:
                metadata = {
                    'selected_model': selected_model,
                    'yolo_confidence': yolo_confidence,
                    'num_detections': len(detections),
                    'image_size': (width, height),
                    'query': query
                }
                return detections, metadata
            else:
                return detections

        except Exception as e:
            print(f"❌ Error in detect_objects: {e}")
            traceback.print_exc()
            self.failed_queries += 1
            
            if return_metadata:
                return [], {'error': str(e)}
            else:
                return []

    def _convert_to_8point_obb(
        self,
        cx: float,
        cy: float,
        w: float,
        h: float,
        angle_rad: float,
        img_w: int,
        img_h: int
    ) -> List[float]:
         
        # Compute corner points in local coordinate system
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Half dimensions
        hw = w / 2.0
        hh = h / 2.0
        
        # Four corners (top-left, top-right, bottom-right, bottom-left)
        corners = np.array([
            [-hw, -hh],  # top-left
            [hw, -hh],   # top-right
            [hw, hh],    # bottom-right
            [-hw, hh]    # bottom-left
        ])
        
        # Rotation matrix
        R = np.array([
            [cos_a, -sin_a],
            [sin_a, cos_a]
        ])
        
        # Rotate and translate to center
        rotated = corners @ R.T
        rotated[:, 0] += cx
        rotated[:, 1] += cy
        
        # Normalize coordinates
        normalized = np.zeros(8)
        for i in range(4):
            normalized[i*2] = rotated[i, 0] / img_w      # x coordinate
            normalized[i*2 + 1] = rotated[i, 1] / img_h  # y coordinate
        
        # Clip to [0, 1] range
        normalized = np.clip(normalized, 0.0, 1.0)
        
        return normalized.tolist()

    def _run_yolo_inference(
        self,
        image: Image.Image,
        query: str
    ) -> Tuple[List[Tuple[str, List[float]]], float]:
        
        try:
            print("🤖 Running YOLO inference...")
            
            # Convert PIL to numpy for YOLO
            image_np = np.array(image)
            img_w, img_h = image.size
            
            # Run inference
            results = self.yolo_model.predict(
                image_np,
                conf=self.yolo_conf_threshold,
                verbose=False
            )
            
            detections = []
            max_conf = 0.0
            
            if len(results) > 0 and len(results[0].obb) > 0:
                boxes = results[0].obb
                
                for idx, (box, conf) in enumerate(zip(boxes.xywhr, boxes.conf), 1):
                    cx, cy, w, h, angle_rad = box.cpu().numpy()
                    confidence = float(conf.cpu().numpy())
                    
                    # Convert to 8-point normalized OBB format
                    obb_8point = self._convert_to_8point_obb(
                        cx, cy, w, h, angle_rad, img_w, img_h
                    )
                    
                    detections.append((
                        str(idx),
                        obb_8point
                    ))
                    
                    max_conf = max(max_conf, confidence)
                
                print(f"  📊 YOLO: {len(detections)} detections, max conf: {max_conf:.3f}")
                print(f"  📐 OBB format: 8-point normalized coordinates")
            else:
                print(f"  ⚠️  YOLO: No detections above {self.yolo_conf_threshold}")
            
            return detections, max_conf

        except Exception as e:
            print(f"❌ YOLO inference failed: {e}")
            traceback.print_exc()
            return [], 0.0

    def _run_geoground_inference(
        self,
        image: Image.Image,
        query: str,
        max_boxes: int = 10
    ) -> List[Tuple[str, List[float]]]:
        """Run GeoGround (LLaVA) inference"""
        try:
            print("🤖 Running GeoGround inference...")
            
            if self.DEFAULT_IMAGE_TOKEN not in query:
                prompt = f"{self.DEFAULT_IMAGE_TOKEN}\n{query}"
            else:
                prompt = query

            conv = self.conv_templates[self.conv_mode].copy()
            conv.append_message(conv.roles[0], prompt)
            conv.append_message(conv.roles[1], None)
            prompt_text = conv.get_prompt()

            input_ids = self.tokenizer_image_token(
                prompt_text,
                self.tokenizer,
                self.IMAGE_TOKEN_INDEX,
                return_tensors="pt"
            )

            if input_ids.dim() == 1:
                input_ids = input_ids.unsqueeze(0)

            input_ids = input_ids.to(self.device)

            image_tensor = self.image_processor.preprocess(
                image,
                return_tensors='pt'
            )['pixel_values'][0]

            if self.device == 'cuda':
                image_tensor = image_tensor.to(dtype=torch.float16).to(self.device)
            else:
                image_tensor = image_tensor.to(dtype=torch.float32).to(self.device)

            with torch.inference_mode():
                pad_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
                
                output_ids = self.geoground_model.generate(
                    input_ids=input_ids,
                    images=image_tensor.unsqueeze(0),
                    do_sample=False,
                    max_new_tokens=512,
                    use_cache=True,
                    pad_token_id=pad_id
                )

            response = self.tokenizer.decode(
                output_ids[0, input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()

            print(f"  📝 GeoGround response: {response[:100]}...")

            img_w, img_h = image.size
            detections = self._parse_geoground_response(response, max_boxes, (img_w, img_h))
            
            print(f"  📊 GeoGround: {len(detections)} detections parsed")
            
            return detections

        except Exception as e:
            print(f"❌ GeoGround inference failed: {e}")
            traceback.print_exc()
            return []

    def _parse_geoground_response(
        self,
        response: str,
        max_boxes: int = 10,
        image_size: Tuple[int, int] = (1000, 1000)
    ) -> List[Tuple[str, List[float]]]:
         
        detections = []
        img_w, img_h = image_size

        obb_pattern = r'<obb>\s*\[([^\]]+)\]\s*</obb>'
        obb_matches = re.findall(obb_pattern, response, re.IGNORECASE)

        for idx, match in enumerate(obb_matches[:max_boxes], 1):
            try:
                coords = [float(x.strip()) for x in match.split(',')]
                if len(coords) >= 5:
                    cx, cy, w, h, angle_deg = coords[:5]
                    
                    cx_px = (cx / 1000.0) * img_w
                    cy_px = (cy / 1000.0) * img_h
                    w_px = (w / 1000.0) * img_w
                    h_px = (h / 1000.0) * img_h
                    angle_rad = np.radians(angle_deg)
                    
                    obb_8point = self._convert_to_8point_obb(
                        cx_px, cy_px, w_px, h_px, angle_rad, img_w, img_h
                    )
                    
                    detections.append((str(idx), obb_8point))
            except (ValueError, IndexError) as e:
                print(f"  ⚠️  Failed to parse OBB: {e}")
                continue

        if not detections:
            hbb_pattern = r'<hbb>\s*\[([^\]]+)\]\s*</hbb>'
            hbb_matches = re.findall(hbb_pattern, response, re.IGNORECASE)

            for idx, match in enumerate(hbb_matches[:max_boxes], 1):
                try:
                    coords = [float(x.strip()) for x in match.split(',')]
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = coords[:4]
                        
                        x1_px = (x1 / 1000.0) * img_w
                        y1_px = (y1 / 1000.0) * img_h
                        x2_px = (x2 / 1000.0) * img_w
                        y2_px = (y2 / 1000.0) * img_h
                        
                        cx_px = (x1_px + x2_px) / 2.0
                        cy_px = (y1_px + y2_px) / 2.0
                        w_px = abs(x2_px - x1_px)
                        h_px = abs(y2_px - y1_px)
                        
                        obb_8point = self._convert_to_8point_obb(
                            cx_px, cy_px, w_px, h_px, 0.0, img_w, img_h
                        )
                        
                        detections.append((str(idx), obb_8point))
                except (ValueError, IndexError) as e:
                    print(f"  ⚠️  Failed to parse HBB: {e}")
                    continue

        if not detections:
            print("  ⚠️  No valid bounding boxes parsed from response")
        else:
            print(f"  📐 Parsed {len(detections)} boxes in 8-point OBB format")

        return detections
         

    def get_statistics(self) -> Dict:
        """Get service usage statistics"""
        success_rate = (
            (self.total_queries - self.failed_queries) / self.total_queries * 100
            if self.total_queries > 0 else 0.0
        )

        yolo_percentage = (
            self.yolo_selections / self.total_queries * 100
            if self.total_queries > 0 else 0.0
        )

        geoground_percentage = (
            self.geoground_selections / self.total_queries * 100
            if self.total_queries > 0 else 0.0
        )

        return {
            "total_queries": self.total_queries,
            "total_detections": self.total_detections,
            "failed_queries": self.failed_queries,
            "success_rate": f"{success_rate:.2f}%",
            "yolo_selections": self.yolo_selections,
            "yolo_percentage": f"{yolo_percentage:.2f}%",
            "geoground_selections": self.geoground_selections,
            "geoground_percentage": f"{geoground_percentage:.2f}%",
            "avg_detections_per_query": (
                self.total_detections / (self.total_queries - self.failed_queries)
                if (self.total_queries - self.failed_queries) > 0 else 0.0
            ),
            "device": str(self.device),
            "yolo_loaded": self.yolo_model is not None,
            "geoground_loaded": self.geoground_model is not None
        }

    def cleanup(self):
        """Cleanup resources and print statistics"""
        try:
            print("\n" + "=" * 80)
            print("🧹 GROUNDING SERVICE CLEANUP")
            print("=" * 80)
            
            stats = self.get_statistics()
            print("\n📊 FINAL STATISTICS:")
            print(json.dumps(stats, indent=2))
            print("=" * 80)

            if self.yolo_model is not None:
                del self.yolo_model
                self.yolo_model = None

            if self.geoground_model is not None:
                del self.geoground_model
                self.geoground_model = None

            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None

            if self.image_processor is not None:
                del self.image_processor
                self.image_processor = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            print("✅ Cleanup complete\n")

        except Exception as e:
            print(f"⚠️  Cleanup error: {e}")


_grounding_service = None


def get_grounding_service(
    yolo_model_path: str = "training_output/vrsbench_v2_obb2/weights/best.pt",
    geoground_model_path: str = "geo_kabir/GeoGround/llava-v1.5-7b-task-geoground",
    device: str = None,
    yolo_conf_threshold: float = 0.4,
    selection_threshold: float = 0.6,
    config: dict = None,
    force_reload: bool = False
) -> GroundingService:
    """
    Get or create global grounding service instance (singleton pattern)
    
    Args:
        yolo_model_path: Path to YOLO model
        geoground_model_path: Path to GeoGround model
        device: Device to use
        yolo_conf_threshold: YOLO confidence threshold
        selection_threshold: Model selection threshold
        config: Additional configuration
        force_reload: Force recreation of service
        
    Returns:
        GroundingService instance
    """
    global _grounding_service

    if _grounding_service is None or force_reload:
        _grounding_service = GroundingService(
            yolo_model_path=yolo_model_path,
            geoground_model_path=geoground_model_path,
            device=device,
            yolo_conf_threshold=yolo_conf_threshold,
            selection_threshold=selection_threshold,
            config=config
        )

    return _grounding_service


def cleanup_grounding_service():
    """Cleanup global grounding service instance"""
    global _grounding_service
    if _grounding_service is not None:
        _grounding_service.cleanup()
        _grounding_service = None


# Example usage and testing
if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 GROUNDING SERVICE TEST")
    print("=" * 80)
    
    # Initialize service
    service = get_grounding_service(
        yolo_model_path="training_output/vrsbench_v2_obb2/weights/best.pt",
        geoground_model_path="geo_kabir/GeoGround/llava-v1.5-7b-task-geoground",
        yolo_conf_threshold=0.4,
        selection_threshold=0.6
    )
    
    # Test with sample query
    test_image = "geo_kabir/data/images_val/P1443_0033.png"
    test_query = "Locate all the small vehicles in the satellite image."
    
    if os.path.exists(test_image):
        print(f"\n🧪 Testing with: {test_image}")
        print(f"Query: {test_query}")
        
        detections, metadata = service.detect_objects(
            test_image,
            test_query,
            return_metadata=True
        )
        
        print(f"\n📊 Results:")
        print(f"  Model used: {metadata['selected_model']}")
        print(f"  Detections: {len(detections)}")
        print(f"  OBB Format: 8-point normalized (x1,y1,x2,y2,x3,y3,x4,y4)")
        
        for label, bbox in detections[:3]:  # Show first 3
            print(f"    {label}: [{bbox[0]:.3f},{bbox[1]:.3f},{bbox[2]:.3f},{bbox[3]:.3f},{bbox[4]:.3f},{bbox[5]:.3f},{bbox[6]:.3f},{bbox[7]:.3f}]")
    

    # Print statistics and cleanup
    cleanup_grounding_service()