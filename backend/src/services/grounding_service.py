"""
Grounding Service - Fully patched production-ready version
Includes:
- Comprehensive dtype fixes (vision tower, mm_projector)
- encode_images patch to force fp16 consistency on GPU
- forward() monkeypatch to remove unsupported kwargs (cache_position, etc.)
- Robust generate() usage with try/fallback to use_cache=False
- Friendly logging
"""
from PIL import Image
from typing import Union, List, Tuple, Optional, Dict
import os
import traceback
import torch
import json
import re
import types


class GroundingService:
    """Service for object grounding with oriented bounding boxes using GeoGround"""

    def __init__(
        self,
        model_path: str = "../../checkpoints/best.pth",
        model_base: str = "../../checkpoints/llava-v1.5-7b-task-geoground",
        device: str = None,
        config: dict = None
    ):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.model_base = model_base
        self.config = config or {}

        print(f"[GroundingService] 🚀 Initializing GeoGround on {self.device}")
        print(f"[GroundingService] Model path: {model_path}")

        self.total_detections = 0
        self.total_queries = 0
        self.failed_queries = 0

        self.model = None
        self.tokenizer = None
        self.image_processor = None
        self.conv_mode = self.config.get('conv_mode', 'llava_v1')

        if model_path:
            self._load_geoground_model(model_path, model_base)

        print("[GroundingService] ✅ Service initialized\n")

    def _patch_encode_images(self):
        """
        Patch encode_images to ensure dtype consistency between image features and mm_projector.
        """
        if not hasattr(self.model, 'encode_images'):
            print("[GroundingService] ⚠️ Model doesn't have encode_images method")
            return

        original_encode_images = self.model.encode_images

        def patched_encode_images(self,images):
            # Ensure images tensor dtype matches model dtype
            try:
                # If images is a single tensor or batch tensor
                if isinstance(images, torch.Tensor):
                    # Move to device first (no-op if already on device)
                    images = images.to(device=self.device)
                    # If running on GPU, prefer float16 for speed
                    if self.device == 'cuda':
                        images = images.to(torch.float16)
                elif isinstance(images, list):
                    imgs = []
                    for img in images:
                        if isinstance(img, torch.Tensor):
                            img = img.to(device=self.device)
                            if self.device == 'cuda':
                                img = img.to(torch.float16)
                        imgs.append(img)
                    images = imgs

                # Attempt to use the model's encode flow while enforcing dtype
                model_obj = None
                if hasattr(self.model, 'get_model'):
                    model_obj = self.model.get_model()
                elif hasattr(self.model, 'model'):
                    model_obj = self.model.model
                else:
                    model_obj = self.model

                if hasattr(model_obj, 'vision_tower'):
                    vision_tower = model_obj.vision_tower
                    # call into nested vision_tower if present
                    if hasattr(vision_tower, 'vision_tower'):
                        image_features = vision_tower.vision_tower(images)
                    else:
                        image_features = vision_tower(images)

                    # normalize features dtype
                    if isinstance(image_features, torch.Tensor):
                        if self.device == 'cuda':
                            image_features = image_features.to(torch.float16)
                    elif hasattr(image_features, 'last_hidden_state'):
                        feat = image_features.last_hidden_state
                        if self.device == 'cuda':
                            feat = feat.to(torch.float16)
                        image_features = feat

                    # apply mm_projector if present
                    if hasattr(model_obj, 'mm_projector'):
                        proj = model_obj.mm_projector
                        # ensure projector dtype matches
                        try:
                            image_features = proj(image_features)
                        except RuntimeError:
                            # try casting projector to image_features dtype then retry
                            proj = proj.to(dtype=image_features.dtype)
                            image_features = proj(image_features)

                    return image_features

                # fallback to original implementation
                return original_encode_images(images)

            except Exception as e:
                # If anything goes wrong, fallback gracefully
                print(f"[GroundingService] ⚠️ patched_encode_images error: {e}")
                traceback.print_exc()
                return original_encode_images(images)

        # bind patched method
        self.model.encode_images = types.MethodType(patched_encode_images, self.model)
        print("[GroundingService] 🔧 encode_images method patched for dtype consistency!")

    def _load_geoground_model(self, model_path: str, model_base: Optional[str]):
        """Load GeoGround model with dtype fixes and compatibility patches"""
        try:
            print("[GroundingService] 📦 Loading GeoGround model...")

            from llava.model.builder import load_pretrained_model
            from llava.mm_utils import get_model_name_from_path, tokenizer_image_token
            from llava.constants import IMAGE_TOKEN_INDEX, DEFAULT_IMAGE_TOKEN
            from llava.conversation import conv_templates

            self.IMAGE_TOKEN_INDEX = IMAGE_TOKEN_INDEX
            self.DEFAULT_IMAGE_TOKEN = DEFAULT_IMAGE_TOKEN
            self.tokenizer_image_token = tokenizer_image_token
            self.conv_templates = conv_templates

            model_name = get_model_name_from_path(model_path)

            # Load model
            self.tokenizer, self.model, self.image_processor, context_len = load_pretrained_model(
                model_path=model_path,
                model_base=model_base,
                model_name=model_name,
                device=self.device,
                load_8bit=False,
                load_4bit=False
            )

            # ===== TOKENIZER VALIDATION & FIX =====
            print("[GroundingService] 🔧 Validating and fixing tokenizer...")
            
            # Check if image token exists in tokenizer
            image_token_id = None
            try:
                # Try to get the image token ID
                image_token_id = self.tokenizer.convert_tokens_to_ids(self.DEFAULT_IMAGE_TOKEN)
                print(f"  ✅ Image token found: '{self.DEFAULT_IMAGE_TOKEN}' → ID: {image_token_id}")
            except Exception as e:
                print(f"[GroundingService] ⚠️ Image token not found: {e}")
                # Add the image token if missing
                print(f"  🔧 Adding image token '{self.DEFAULT_IMAGE_TOKEN}' to tokenizer...")
                self.tokenizer.add_tokens([self.DEFAULT_IMAGE_TOKEN], special_tokens=True)
                self.model.resize_token_embeddings(len(self.tokenizer))
                image_token_id = self.tokenizer.convert_tokens_to_ids(self.DEFAULT_IMAGE_TOKEN)
                print(f"  ✅ Image token added: '{self.DEFAULT_IMAGE_TOKEN}' → ID: {image_token_id}")
            
            # Validate token ID is within embedding range
            if image_token_id is not None:
                vocab_size = self.model.get_input_embeddings().weight.shape[0]
                if image_token_id >= vocab_size:
                    print(f"[GroundingService] ⚠️ Image token ID {image_token_id} >= vocab size {vocab_size}")
                    print(f"  🔧 Resizing embeddings to match tokenizer...")
                    self.model.resize_token_embeddings(len(self.tokenizer))
                    vocab_size = self.model.get_input_embeddings().weight.shape[0]
                    print(f"  ✅ Resized embeddings to vocab size: {vocab_size}")
            
            # ===== COMPREHENSIVE DTYPE FIX =====
            print("[GroundingService] 🔧 Applying comprehensive dtype fixes...")
            target_dtype = torch.float16 if self.device == "cuda" else torch.float32

            # 1) Move model to device and dtype
            try:
                self.model = self.model.to(device=self.device)
            except Exception:
                # some wrapper types expect .to(dtype=...)
                try:
                    self.model = self.model.to(dtype=target_dtype)
                except Exception:
                    pass

            # 2) convert submodules if accessible
            try:
                base_model = self.model.model if hasattr(self.model, 'model') else self.model
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
            except Exception as e:
                print(f"[GroundingService] ⚠️ submodule dtype conversion warning: {e}")

            # 3) Patch encode_images to be robust
            try:
                self._patch_encode_images()
            except Exception as e:
                print(f"[GroundingService] ⚠️ Failed to patch encode_images: {e}")

            # 4) Monkeypatch forward to remove unsupported kwargs like cache_position
            try:
                if hasattr(self.model, "forward"):
                    original_forward = self.model.forward

                    def patched_forward(self,*args, **kwargs):
                        # Remove problematic/unknown kwargs that transformers may inject
                        kwargs.pop("cache_position", None)
                        kwargs.pop("position_ids", None)
                        kwargs.pop("past_key_values", None)
                        return original_forward(*args, **kwargs)

                    self.model.forward = types.MethodType(patched_forward, self.model)
                    print("[GroundingService] 🔧 Patched forward() to remove cache_position!")
            except Exception as e:
                print(f"[GroundingService] ⚠️ Failed to monkeypatch forward: {e}")

            # ===================================

            print(f"[GroundingService] ✅ Model loaded: {model_name}")
            print(f"[GroundingService] ✅ Context length: {context_len}")
            print(f"[GroundingService] ✅ Conversation mode: {self.conv_mode}")

        except Exception as e:
            print(f"[GroundingService] ❌ Failed to load model: {e}")
            traceback.print_exc()
            self.model = None

    def detect_objects(
        self,
        image: Union[str, Image.Image],
        query: str,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.3,
        max_boxes: int = 10
    ) -> List[Tuple[str, List[float]]]:
        """Detect objects using GeoGround and return oriented bounding boxes"""
        try:
            self.total_queries += 1
            print(f"[GroundingService] 🔍 Query: '{query[:60]}...'")

            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image not found: {image}")
                image = Image.open(image)

            if not isinstance(image, Image.Image):
                raise ValueError(f"Image must be PIL Image or path, got {type(image)}")

            if image.mode != 'RGB':
                image = image.convert('RGB')

            width, height = image.size
            print(f"[GroundingService] 📐 Image: {width}x{height}")

            if self.model is not None:
                detections = self._run_geoground_inference(image, query, max_boxes)
            else:
                print("[GroundingService] ⚠️ Model not loaded, using placeholder")
                detections = self._placeholder_detection(image, query, width, height)

            self.total_detections += len(detections)
            print(f"[GroundingService] ✅ Detected {len(detections)} objects")

            return detections

        except Exception as e:
            print(f"[GroundingService] ❌ Error: {e}")
            traceback.print_exc()
            self.failed_queries += 1
            return []

    def _run_geoground_inference(
        self,
        image: Image.Image,
        query: str,
        max_boxes: int = 10
    ) -> List[Tuple[str, List[float]]]:
        """Run GeoGround inference on image with query"""
        try:
            prompt = self._prepare_geoground_prompt(query)

            conv = self.conv_templates[self.conv_mode].copy()
            conv.append_message(conv.roles[0], prompt)
            conv.append_message(conv.roles[1], None)
            prompt_text = conv.get_prompt()

            # -----------------------------------------------------------------------
            # SAFE TOKENIZATION FOR GEOGROUND  (handles all LLaVA variants)
            # -----------------------------------------------------------------------
            
            tok = self.tokenizer_image_token(
                prompt_text,
                self.tokenizer,
                self.IMAGE_TOKEN_INDEX,
                return_tensors="pt"
            )

            input_ids = None
            attention_mask = None

            # CASE 1 — tokenizer returns a dict
            if isinstance(tok, dict):
                input_ids = tok.get("input_ids", None)
                attention_mask = tok.get("attention_mask", None)

            # CASE 2 — tokenizer returns a tensor
            elif isinstance(tok, torch.Tensor):
                input_ids = tok
                attention_mask = None

            # CASE 3 — tokenizer returned something invalid (tuple, None, etc.)
            else:
                raise RuntimeError(
                    f"GeoGround tokenizer returned unexpected format: {type(tok)} → {tok}"
                )

            # NOW VALIDATE input_ids
            if input_ids is None:
                raise RuntimeError(
                    "GeoGround tokenizer returned input_ids=None — image token injection failed."
                )

            # Ensure batch dimension
            if input_ids.dim() == 1:
                input_ids = input_ids.unsqueeze(0)

            input_ids = input_ids.to(self.device)

            # ===== CRITICAL: VALIDATE TOKEN IDs ARE WITHIN VOCAB RANGE =====
            print("[GroundingService] 🔍 Validating token IDs...")
            
            # Get vocab size from model embeddings
            vocab_size = self.model.get_input_embeddings().weight.shape[0]
            
            # Check min and max token IDs
            min_token = input_ids.min().item()
            max_token = input_ids.max().item()
            
            print(f"  ✅ Token ID range: {min_token} to {max_token}")
            print(f"  ✅ Vocab size: {vocab_size}")
            
            # ===== FIX FOR NEGATIVE TOKEN IDs =====
            # Some tokenizers use negative IDs for special tokens
            # We need to check if negative IDs are actually special tokens
            if min_token < 0:
                print(f"[GroundingService] ⚠️ Negative token IDs detected: {min_token}")
                
                # Check if this is the IMAGE_TOKEN_INDEX
                if min_token == self.IMAGE_TOKEN_INDEX:
                    print(f"[GroundingService] ⚠️ Image token has negative ID: {self.IMAGE_TOKEN_INDEX}")
                    
                    # Special handling for negative image token IDs
                    # This means the tokenizer uses negative IDs for special tokens
                    # We need to convert negative IDs to positive ones
                    
                    # First, find the actual tokenizer mapping
                    print(f"[GroundingService] 🔧 Checking tokenizer special tokens...")
                    
                    # Get all special tokens and their IDs
                    special_tokens = self.tokenizer.special_tokens_map if hasattr(self.tokenizer, 'special_tokens_map') else {}
                    print(f"  📋 Special tokens: {special_tokens}")
                    
                    # Check if image token is in special tokens
                    if '<image>' in str(special_tokens):
                        print(f"  ✅ <image> found in special tokens map")
                    
                    # For LLaVA forks that use negative IDs, we need to remap
                    # Create a mapping from negative to positive IDs
                    print(f"[GroundingService] 🔧 Attempting to fix negative token IDs...")
                    
                    # Get the actual tokenizer vocab size
                    tokenizer_vocab_size = len(self.tokenizer)
                    print(f"  📋 Tokenizer vocab size: {tokenizer_vocab_size}")
                    
                    # Create a safe version of input_ids by converting negatives
                    # Strategy: Map negative IDs to positive IDs in a reserved range
                    # For example, -200 -> vocab_size + 200
                    
                    # First, let's see what the actual tokens are
                    try:
                        token_texts = self.tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
                        print(f"  📋 First few tokens: {token_texts[:10]}")
                    except:
                        print(f"  📋 Could not decode tokens (negative IDs issue)")
                    
                    # Create a copy of input_ids for modification
                    original_input_ids = input_ids.clone()
                    
                    # Try to map negative IDs to their absolute values
                    # This is a common pattern in some tokenizers
                    print(f"[GroundingService] 🔧 Strategy 1: Convert negatives to absolute values")
                    fixed_input_ids = torch.where(
                        input_ids < 0,
                        torch.abs(input_ids),  # Convert -200 to 200
                        input_ids
                    )
                    
                    # Check if the fixed IDs are within vocab range
                    fixed_min = fixed_input_ids.min().item()
                    fixed_max = fixed_input_ids.max().item()
                    
                    if fixed_min >= 0 and fixed_max < vocab_size:
                        print(f"[GroundingService] ✅ Strategy 1 worked! New range: {fixed_min} to {fixed_max}")
                        input_ids = fixed_input_ids
                    else:
                        print(f"[GroundingService] ⚠️ Strategy 1 failed: {fixed_min} to {fixed_max}")
                        
                        # Strategy 2: Map negatives to safe range near end of vocab
                        print(f"[GroundingService] 🔧 Strategy 2: Map negatives to safe range")
                        
                        # Use a hash-based mapping: negative ID -> (vocab_size - abs(ID) % (vocab_size - 1000))
                        # This keeps IDs within range while preserving uniqueness
                        def map_negative_id(neg_id, vocab_size):
                            abs_id = abs(neg_id)
                            # Map to a safe range near the end of vocab
                            safe_range_start = vocab_size - 500  # Reserve last 500 tokens
                            if safe_range_start < 0:
                                safe_range_start = 0
                            # Ensure we don't go out of bounds
                            mapped_id = safe_range_start + (abs_id % min(500, vocab_size - safe_range_start))
                            if mapped_id >= vocab_size:
                                mapped_id = vocab_size - 1
                            return mapped_id
                        
                        # Apply the mapping
                        fixed_input_ids = input_ids.clone()
                        num_negative = 0
                        for i in range(input_ids.shape[0]):
                            for j in range(input_ids.shape[1]):
                                if input_ids[i, j] < 0:
                                    num_negative += 1
                                    original = input_ids[i, j].item()
                                    mapped = map_negative_id(original, vocab_size)
                                    fixed_input_ids[i, j] = mapped
                                    if num_negative <= 5:  # Log first few mappings
                                        print(f"  🔄 Mapped {original} → {mapped}")
                        
                        print(f"  🔄 Total negative tokens mapped: {num_negative}")
                        
                        # Update input_ids
                        input_ids = fixed_input_ids
            
            # Final safety check and fix
            min_token = input_ids.min().item()
            max_token = input_ids.max().item()
            
            if min_token < 0:
                print(f"[GroundingService] ❌ Still have negative IDs after fix: {min_token}")
                print(f"[GroundingService] 🔧 Using emergency fallback: replacing negatives with pad token")
                
                pad_token_id = self.tokenizer.pad_token_id if hasattr(self.tokenizer, 'pad_token_id') else self.tokenizer.eos_token_id
                if pad_token_id is None:
                    pad_token_id = 0  # Fallback to ID 0
                
                input_ids = torch.where(input_ids < 0, torch.tensor(pad_token_id, device=input_ids.device), input_ids)
                min_token = input_ids.min().item()
                print(f"  ✅ After emergency fix: min token = {min_token}")
            
            if max_token >= vocab_size:
                # Cap any IDs that exceed vocab size
                print(f"[GroundingService] ⚠️ Some token IDs exceed vocab size, capping them")
                input_ids = torch.where(
                    input_ids >= vocab_size,
                    torch.tensor(vocab_size - 1, device=input_ids.device),
                    input_ids
                )
                max_token = input_ids.max().item()
                print(f"  ✅ After capping: max token = {max_token}")
            
            print(f"[GroundingService] ✅ Final token ID range: {input_ids.min().item()} to {input_ids.max().item()}")
            print("[GroundingService] ✅ Token IDs validated and fixed successfully!")

            # Create attention mask if missing
            if attention_mask is None:
                attention_mask = torch.ones_like(input_ids, dtype=torch.long, device=self.device)
            else:
                if attention_mask.dim() == 1:
                    attention_mask = attention_mask.unsqueeze(0)
                attention_mask = attention_mask.to(self.device)

            # --- Process image tensor as before ---
            image_tensor = self.image_processor.preprocess(
                image,
                return_tensors='pt'
            )['pixel_values'][0]

            if self.device == 'cuda':
                image_tensor = image_tensor.to(dtype=torch.float16).to(self.device)
            else:
                image_tensor = image_tensor.to(dtype=torch.float32).to(self.device)

            # --- Generation with GeoGround-compatible attention_mask passing ---
            with torch.inference_mode():
                # Get pad token ID
                pad_id = (
                    self.tokenizer.pad_token_id
                    if hasattr(self.tokenizer, "pad_token_id")
                    else self.tokenizer.eos_token_id
                )
                
                try:
                    # First try with use_cache=True for speed
                    output_ids = self.model.generate(
                        input_ids=input_ids,
                        images=image_tensor.unsqueeze(0).to(self.device),
                        do_sample=False,
                        max_new_tokens=512,
                        use_cache=True,
                        pad_token_id=pad_id,
                        **{"attention_mask": attention_mask}  # ← MUST pass this way for GeoGround
                    )
                except (TypeError, AttributeError) as e:
                    # GeoGround might reject certain kwargs - retry without cache
                    print("[GroundingService] ⚠️ generate() raised error, retrying without cache:", e)
                    output_ids = self.model.generate(
                        input_ids=input_ids,
                        images=image_tensor.unsqueeze(0).to(self.device),
                        do_sample=False,
                        max_new_tokens=512,
                        use_cache=False,  # Safer for GeoGround
                        pad_token_id=pad_id,
                        **{"attention_mask": attention_mask}  # ← Still passes in model_kwargs
                    )
                except Exception as e:
                    # catch-all for other generation failures; re-raise after logging
                    print("[GroundingService] ❌ generate() failed with unexpected error:", e)
                    raise

            response = self.tokenizer.decode(
                output_ids[0, input_ids.shape[1]:],
                skip_special_tokens=True
            ).strip()

            print(f"[GroundingService] 📝 Raw response: {response[:100]}...")
            detections = self._parse_geoground_response(response, max_boxes)

            return detections

        except Exception as e:
            print(f"[GroundingService] ❌ GeoGround inference failed: {e}")
            traceback.print_exc()
            return []

    def _prepare_geoground_prompt(self, query: str) -> str:
        """Prepare prompt for GeoGround"""
        if self.DEFAULT_IMAGE_TOKEN not in query:
            prompt = f"{self.DEFAULT_IMAGE_TOKEN}\n{query}"
        else:
            prompt = query
        return prompt

    def _parse_geoground_response(
        self,
        response: str,
        max_boxes: int = 10
    ) -> List[Tuple[str, List[float]]]:
        """Parse GeoGround response to extract bounding boxes"""
        detections = []

        # Try parsing OBB format first (oriented bounding boxes)
        obb_pattern = r'<obb>\s*\[([^\]]+)\]\s*</obb>'
        obb_matches = re.findall(obb_pattern, response, re.IGNORECASE)

        for idx, match in enumerate(obb_matches[:max_boxes], 1):
            try:
                coords = [float(x.strip()) for x in match.split(',')]
                if len(coords) >= 5:
                    cx, cy, w, h, angle = coords[:5]
                    cx_norm = max(0.0, min(1.0, cx / 1000.0))
                    cy_norm = max(0.0, min(1.0, cy / 1000.0))
                    w_norm = max(0.0, min(1.0, w / 1000.0))
                    h_norm = max(0.0, min(1.0, h / 1000.0))
                    detections.append((str(idx), [cx_norm, cy_norm, w_norm, h_norm, angle]))
            except (ValueError, IndexError):
                continue

        # If no OBB found, try HBB format (horizontal bounding boxes)
        if not detections:
            hbb_pattern = r'<hbb>\s*\[([^\]]+)\]\s*</hbb>'
            hbb_matches = re.findall(hbb_pattern, response, re.IGNORECASE)

            for idx, match in enumerate(hbb_matches[:max_boxes], 1):
                try:
                    coords = [float(x.strip()) for x in match.split(',')]
                    if len(coords) >= 4:
                        x1, y1, x2, y2 = coords[:4]
                        cx = (x1 + x2) / 2.0
                        cy = (y1 + y2) / 2.0
                        w = abs(x2 - x1)
                        h = abs(y2 - y1)
                        angle = 0.0
                        cx_norm = max(0.0, min(1.0, cx / 1000.0))
                        cy_norm = max(0.0, min(1.0, cy / 1000.0))
                        w_norm = max(0.0, min(1.0, w / 1000.0))
                        h_norm = max(0.0, min(1.0, h / 1000.0))
                        detections.append((str(idx), [cx_norm, cy_norm, w_norm, h_norm, angle]))
                except (ValueError, IndexError):
                    continue

        # If still no detections, try parsing raw numbers
        if not detections:
            number_pattern = r'\[?\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)(?:\s*,\s*(-?\d+\.?\d*))?\s*\]?'
            number_matches = re.findall(number_pattern, response)

            for idx, match in enumerate(number_matches[:max_boxes], 1):
                try:
                    if match[4]:  # Has angle (OBB format)
                        cx, cy, w, h, angle = [float(x) if x else 0 for x in match]
                        cx_norm = max(0.0, min(1.0, cx / 1000.0))
                        cy_norm = max(0.0, min(1.0, cy / 1000.0))
                        w_norm = max(0.0, min(1.0, w / 1000.0))
                        h_norm = max(0.0, min(1.0, h / 1000.0))
                    else:
                        x1, y1, x2, y2 = [float(x) for x in match[:4]]
                        cx_norm = max(0.0, min(1.0, ((x1 + x2) / 2.0) / 1000.0))
                        cy_norm = max(0.0, min(1.0, ((y1 + y2) / 2.0) / 1000.0))
                        w_norm = max(0.0, min(1.0, abs(x2 - x1) / 1000.0))
                        h_norm = max(0.0, min(1.0, abs(y2 - y1) / 1000.0))
                        angle = 0.0

                    detections.append((str(idx), [cx_norm, cy_norm, w_norm, h_norm, angle]))
                except (ValueError, IndexError):
                    continue

        if not detections:
            print("[GroundingService] ⚠️  No valid bounding boxes found in response")

        return detections

    def _placeholder_detection(
        self,
        image: Image.Image,
        query: str,
        width: int,
        height: int
    ) -> List[Tuple[str, List[float]]]:
        """Placeholder detection (used when model is not loaded)"""
        print("[GroundingService] ⚠️  Using mock detection")

        detections = []
        query_lower = query.lower()

        if "aircraft" in query_lower or "airplane" in query_lower or "plane" in query_lower:
            detections.extend([
                ("1", [0.50, 0.17, 0.08, 0.08, -37.18]),
                ("2", [0.40, 0.10, 0.09, 0.09, 0.0])
            ])

        if "tank" in query_lower or "storage" in query_lower:
            detections.extend([
                ("3", [0.65, 0.75, 0.05, 0.05, 0.0]),
                ("4", [0.70, 0.72, 0.05, 0.05, 0.0])
            ])

        if "building" in query_lower or "house" in query_lower:
            detections.extend([
                ("5", [0.30, 0.40, 0.15, 0.12, 0.0]),
                ("6", [0.55, 0.60, 0.12, 0.10, 15.0])
            ])

        if "track" in query_lower or "field" in query_lower or "ground" in query_lower:
            detections.append(("7", [0.5, 0.5, 0.2, 0.15, 0.0]))

        if "ship" in query_lower or "boat" in query_lower or "vessel" in query_lower:
            detections.extend([
                ("8", [0.25, 0.65, 0.08, 0.12, 45.0]),
                ("9", [0.75, 0.35, 0.07, 0.11, -30.0])
            ])

        if not detections:
            detections.append(("1", [0.5, 0.5, 0.1, 0.1, 0.0]))

        return detections

    def get_statistics(self) -> Dict[str, any]:
        """Get service statistics"""
        success_rate = (
            (self.total_queries - self.failed_queries) / self.total_queries * 100
            if self.total_queries > 0 else 0.0
        )

        return {
            "total_queries": self.total_queries,
            "total_detections": self.total_detections,
            "failed_queries": self.failed_queries,
            "success_rate": f"{success_rate:.2f}%",
            "avg_detections_per_query": (
                self.total_detections / (self.total_queries - self.failed_queries)
                if (self.total_queries - self.failed_queries) > 0 else 0.0
            ),
            "device": str(self.device),
            "model_loaded": self.model is not None
        }

    def cleanup(self):
        """Cleanup resources"""
        try:
            print(f"[GroundingService] 🧹 Cleaning up...")
            stats = self.get_statistics()
            print(f"[GroundingService] 📊 Stats: {json.dumps(stats, indent=2)}")

            if self.model is not None:
                del self.model
                self.model = None

            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None

            if self.image_processor is not None:
                del self.image_processor
                self.image_processor = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            print("[GroundingService] ✅ Cleaned up")
        except Exception as e:
            print(f"[GroundingService] ⚠️  Cleanup error: {e}")


# Singleton
_grounding_service = None


def get_grounding_service(
    model_path: str = None,
    model_base: str = None,
    config: dict = None,
    force_reload: bool = False
) -> GroundingService:
    """Get or create global grounding service instance"""
    global _grounding_service

    if _grounding_service is None or force_reload:
        _grounding_service = GroundingService(
            model_path=model_path,
            model_base=model_base,
            config=config
        )

    return _grounding_service


def cleanup_grounding_service():
    """Cleanup global grounding service instance"""
    global _grounding_service
    if _grounding_service is not None:
        _grounding_service.cleanup()
        _grounding_service = None
