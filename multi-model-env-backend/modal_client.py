"""
Modal Backend Client
Sends requests to Modal-deployed AI services (Caption, VQA, Grounding)
"""
import requests
import json
from typing import Optional, Dict, List, Union
from pathlib import Path


class ModalClient:
    """Client for interacting with Modal-deployed GeoNLI backend"""
    
    def __init__(self, modal_url: str):
        """
        Initialize Modal client
        
        Args:
            modal_url: Base URL of Modal deployment (e.g., https://your-app.modal.run)
        """
        self.modal_url = modal_url.rstrip('/')
        self.session = requests.Session()
        
        print(f"✅ Modal Client initialized: {self.modal_url}")
    
    def health_check(self) -> Dict:
        """Check if Modal backend is healthy"""
        try:
            response = self.session.get(f"{self.modal_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "unhealthy"}
    
    # =========================================================================
    # INDIVIDUAL SERVICE ENDPOINTS (Direct Modal Functions)
    # =========================================================================
    
    def caption_image(
        self, 
        image_path: str,
        max_tokens: int = 512,
        temperature: float = 0.7
    ) -> Dict:
        """
        Generate caption for satellite image using Florence-2
        
        Args:
            image_path: Path to image file
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            {"caption": "Generated caption text"}
        """
        try:
            print(f"📝 Requesting caption for: {image_path}")
            
            # For Modal deployment, you'd upload the image or provide URL
            # This example assumes image_path is accessible to Modal
            
            request_data = {
                "service": "caption",
                "image": image_path,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = self.session.post(
                f"{self.modal_url}/router",
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Caption generated: {result.get('caption', '')[:100]}...")
            return result
            
        except Exception as e:
            print(f"❌ Caption request failed: {e}")
            return {"error": str(e)}
    
    def answer_question(
        self,
        image_path: str,
        question: str,
        max_tokens: int = 128,
        temperature: float = 0.7
    ) -> Dict:
        """
        Answer question about satellite image using Florence-2 VQA
        
        Args:
            image_path: Path to image file
            question: Question to answer
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            {"answer": "Answer text"}
        """
        try:
            print(f"❓ Asking: {question}")
            
            request_data = {
                "service": "vqa",
                "image": image_path,
                "query": question,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = self.session.post(
                f"{self.modal_url}/router",
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            print(f"✅ Answer: {result.get('answer', '')}")
            return result
            
        except Exception as e:
            print(f"❌ VQA request failed: {e}")
            return {"error": str(e)}
    
    def detect_objects(
        self,
        image_path: str,
        query: str,
        max_boxes: int = 10
    ) -> Dict:
        """
        Detect objects in satellite image using GeoGround
        
        Args:
            image_path: Path to image file
            query: Natural language query describing objects
            max_boxes: Maximum number of boxes to return
            
        Returns:
            {"detections": [{"object_id": "1", "obbox": [...]}]}
        """
        try:
            print(f"🎯 Detecting: {query}")
            
            request_data = {
                "service": "grounding",
                "image": image_path,
                "query": query,
                "max_boxes": max_boxes
            }
            
            response = self.session.post(
                f"{self.modal_url}/router",
                json=request_data,
                timeout=120  # Grounding can take longer
            )
            response.raise_for_status()
            
            result = response.json()
            num_detections = len(result.get('detections', []))
            print(f"✅ Detected {num_detections} objects")
            return result
            
        except Exception as e:
            print(f"❌ Grounding request failed: {e}")
            return {"error": str(e)}
    
    # =========================================================================
    # GEONLI EVALUATION ENDPOINT (Complete Pipeline)
    # =========================================================================
    
    def evaluate_geonli(
        self,
        image_url: str,
        image_id: str,
        width: int,
        height: int,
        spatial_resolution_m: float,
        caption_instruction: Optional[str] = None,
        grounding_instruction: Optional[str] = None,
        binary_question: Optional[str] = None,
        numeric_question: Optional[str] = None,
        semantic_question: Optional[str] = None
    ) -> Dict:
        """
        Complete GeoNLI evaluation with all query types
        
        Args:
            image_url: URL to image
            image_id: Unique image identifier
            width: Image width in pixels
            height: Image height in pixels
            spatial_resolution_m: Spatial resolution in meters
            caption_instruction: Caption generation instruction
            grounding_instruction: Object detection instruction
            binary_question: Yes/No question
            numeric_question: Count question
            semantic_question: Descriptive question
            
        Returns:
            Complete evaluation response with all results
        """
        try:
            print("\n" + "="*80)
            print("🚀 GEONLI EVALUATION REQUEST")
            print("="*80)
            print(f"Image ID: {image_id}")
            print(f"Image URL: {image_url}")
            print(f"Dimensions: {width}x{height}")
            print(f"Resolution: {spatial_resolution_m}m")
            
            # Build request payload
            request_payload = {
                "input_image": {
                    "image_id": image_id,
                    "image_url": image_url,
                    "metadata": {
                        "width": width,
                        "height": height,
                        "spatial_resolution_m": spatial_resolution_m
                    }
                },
                "queries": {}
            }
            
            # Add caption query if provided
            if caption_instruction:
                request_payload["queries"]["caption_query"] = {
                    "instruction": caption_instruction
                }
                print(f"📝 Caption query: {caption_instruction[:60]}...")
            
            # Add grounding query if provided
            if grounding_instruction:
                request_payload["queries"]["grounding_query"] = {
                    "instruction": grounding_instruction
                }
                print(f"🎯 Grounding query: {grounding_instruction[:60]}...")
            
            # Add attribute queries if provided
            attribute_query = {}
            if binary_question:
                attribute_query["binary"] = {"instruction": binary_question}
                print(f"❓ Binary: {binary_question[:60]}...")
            
            if numeric_question:
                attribute_query["numeric"] = {"instruction": numeric_question}
                print(f"🔢 Numeric: {numeric_question[:60]}...")
            
            if semantic_question:
                attribute_query["semantic"] = {"instruction": semantic_question}
                print(f"💬 Semantic: {semantic_question[:60]}...")
            
            if attribute_query:
                request_payload["queries"]["attribute_query"] = attribute_query
            
            print("="*80)
            
            # Send request to Modal backend
            response = self.session.post(
                f"{self.modal_url}/geoNLI/eval",
                json=request_payload,
                timeout=180  # 3 minutes for complete evaluation
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Print summary
            print("\n✅ EVALUATION COMPLETED")
            print("="*80)
            
            if "queries" in result:
                queries_result = result["queries"]
                
                if "caption_query" in queries_result:
                    caption = queries_result["caption_query"]["response"]
                    print(f"📝 Caption: {caption[:100]}...")
                
                if "grounding_query" in queries_result:
                    detections = queries_result["grounding_query"]["response"]
                    print(f"🎯 Grounding: {len(detections)} objects detected")
                
                if "attribute_query" in queries_result:
                    attr = queries_result["attribute_query"]
                    if "binary" in attr:
                        print(f"❓ Binary: {attr['binary']['response']}")
                    if "numeric" in attr:
                        print(f"🔢 Numeric: {attr['numeric']['response']}")
                    if "semantic" in attr:
                        print(f"💬 Semantic: {attr['semantic']['response'][:50]}...")
            
            print("="*80 + "\n")
            
            return result
            
        except Exception as e:
            print(f"❌ GeoNLI evaluation failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_client(modal_url: str) -> ModalClient:
    """
    Create Modal client instance
    
    Args:
        modal_url: Modal deployment URL
        
    Returns:
        ModalClient instance
    """
    return ModalClient(modal_url)


def test_modal_services(modal_url: str, test_image: str = None):
    """
    Test all Modal services
    
    Args:
        modal_url: Modal deployment URL
        test_image: Path to test image (optional)
    """
    client = create_client(modal_url)
    
    print("\n" + "="*80)
    print("🧪 TESTING MODAL SERVICES")
    print("="*80)
    
    # Health check
    print("\n1️⃣ Health Check")
    health = client.health_check()
    print(f"Status: {health}")
    
    if test_image:
        # Test caption
        print("\n2️⃣ Testing Caption Service")
        caption_result = client.caption_image(test_image)
        print(f"Result: {caption_result}")
        
        # Test VQA
        print("\n3️⃣ Testing VQA Service")
        vqa_result = client.answer_question(
            test_image,
            "What objects are visible in this image?"
        )
        print(f"Result: {vqa_result}")
        
        # Test Grounding
        print("\n4️⃣ Testing Grounding Service")
        grounding_result = client.detect_objects(
            test_image,
            "Locate all buildings in the image"
        )
        print(f"Result: {grounding_result}")
    
    print("\n" + "="*80)
    print("✅ TESTING COMPLETE")
    print("="*80)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    import sys
    
    # Example 1: Full GeoNLI Evaluation
    print("\n📋 Example 1: Full GeoNLI Evaluation")
    print("-" * 80)
    
    MODAL_URL = "https://your-app--multi-model-env-backend.modal.run"
    
    client = create_client(MODAL_URL)
    
    # Complete evaluation
    result = client.evaluate_geonli(
        image_url="https://bit.ly/4ouV45l",
        image_id="sample1.png",
        width=512,
        height=512,
        spatial_resolution_m=1.57,
        caption_instruction="Generate a detailed caption describing all visible elements in the satellite image.",
        grounding_instruction="Locate and return oriented bounding boxes for all storage tanks visible in the image.",
        binary_question="Is there any digit present in the image?",
        numeric_question="How many storage tanks are visible?",
        semantic_question="What is the color of the digit if present?"
    )
    
    # Save result to file
    with open("geonli_result.json", "w") as f:
        json.dump(result, f, indent=2)
    print("\n💾 Result saved to: geonli_result.json")
    
    
    # Example 2: Individual Services
    print("\n\n📋 Example 2: Individual Services")
    print("-" * 80)
    
    # Caption only
    caption_result = client.caption_image(
        image_path="/path/to/satellite_image.jpg"
    )
    print(f"Caption: {caption_result}")
    
    # VQA only
    vqa_result = client.answer_question(
        image_path="/path/to/satellite_image.jpg",
        question="How many cars are in the parking lot?"
    )
    print(f"Answer: {vqa_result}")
    
    # Grounding only
    grounding_result = client.detect_objects(
        image_path="/path/to/satellite_image.jpg",
        query="Locate all airplanes on the runway"
    )
    print(f"Detections: {grounding_result}")
    
    
    # Example 3: Test all services
    print("\n\n📋 Example 3: Test All Services")
    print("-" * 80)
    
    test_modal_services(
        modal_url=MODAL_URL,
        test_image="/path/to/test_image.jpg"
    )