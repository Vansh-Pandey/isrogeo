"""
Florence-2 Caption Service
Handles detailed caption generation for satellite images
"""
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from peft import PeftModel
from typing import Union
import os


class Florence2CaptionService:
    """Service for generating detailed captions using Florence-2"""
    
    def __init__(
        self,
        model_path: str = "../../checkpoints/caption_model",
        base_model: str = "microsoft/Florence-2-large",
        device: str = None
    ):
        """
        Initialize Florence-2 caption service
        
        Args:
            model_path: Path to LoRA checkpoint (optional)
            base_model: Base Florence-2 model name
            device: Device to run on ('cuda', 'cpu', or None for auto)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"[Florence2CaptionService] Initializing on {self.device}")
        
        # Load processor
        print(f"[Florence2CaptionService] Loading processor from {base_model}")
        self.processor = AutoProcessor.from_pretrained(
            base_model,
            trust_remote_code=True
        )
        
        # Configure tokenizer
        if getattr(self.processor.tokenizer, "pad_token", None) is None:
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
        
        # Load base model
        print(f"[Florence2CaptionService] Loading base model: {base_model}")
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            trust_remote_code=True,
            torch_dtype=torch.float32,
            device_map=None,
            low_cpu_mem_usage=False,
            attn_implementation="eager"
        )
        
        # Load LoRA weights if provided
        if model_path and os.path.exists(model_path):
            print(f"[Florence2CaptionService] Loading LoRA weights from {model_path}")
            try:
                self.model = PeftModel.from_pretrained(
                    self.model,
                    model_path,
                    is_trainable=False
                )
                print("[Florence2CaptionService] ✅ LoRA adapter loaded")
            except Exception as e:
                print(f"[Florence2CaptionService] ⚠ LoRA loading failed: {e}")
                print("[Florence2CaptionService] Using base model only")
        
        # Move to device
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Caption prompt (using detailed captioning task)
        self.caption_prompt = '<MORE_DETAILED_CAPTION>'
        
        print("[Florence2CaptionService] ✅ Service initialized\n")
    
    def preprocess_image(self, image: Union[str, Image.Image]) -> Image.Image:
        """
        Load and preprocess image
        
        Args:
            image: Path to image or PIL Image
            
        Returns:
            PIL Image in RGB format
        """
        if isinstance(image, str):
            image = Image.open(image)
        
        if not isinstance(image, Image.Image):
            raise ValueError(f"Image must be a file path or PIL Image, got {type(image)}")
        
        # Convert to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    
    def generate_caption(
        self,
        image: Union[str, Image.Image],
        max_new_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generate detailed caption for satellite image
        
        Args:
            image: Image path or PIL Image
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated caption as string
        """
        try:
            # Preprocess image
            image = self.preprocess_image(image)
            
            # Prepare inputs
            inputs = self.processor(
                text=self.caption_prompt,
                images=image,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate caption
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature if temperature > 0 else 1.0,
                    do_sample=True if temperature > 0 else False,
                    pad_token_id=self.processor.tokenizer.pad_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id,
                    use_cache=False,
                    num_beams=1
                )
            
            # Decode caption
            generated_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            # Extract caption (remove prompt if present)
            caption = generated_text.replace(self.caption_prompt, "").strip()
            
            if not caption:
                caption = "Unable to generate caption"
            
            return caption
            
        except Exception as e:
            print(f"[Florence2CaptionService] Error in generate_caption: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            del self.model
            del self.processor
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            print("[Florence2CaptionService] Resources cleaned up")
        except Exception as e:
            print(f"[Florence2CaptionService] Cleanup error: {e}")


# Global service instance (singleton pattern)
_caption_service = None


def get_caption_service(
    model_path: str = None,
    force_reload: bool = False
) -> Florence2CaptionService:
    """
    Get or create global caption service instance
    
    Args:
        model_path: Path to LoRA checkpoint
        force_reload: Force reload the service
        
    Returns:
        Florence2CaptionService instance
    """
    global _caption_service
    
    if _caption_service is None or force_reload:
        _caption_service = Florence2CaptionService(model_path=model_path)
    
    return _caption_service