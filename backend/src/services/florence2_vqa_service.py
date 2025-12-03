"""
Florence-2 VQA Service (Complete Production Version)
Handles Visual Question Answering for attribute queries (binary, numeric, semantic)

Features:
- Batch processing for multiple questions
- Answer normalization and parsing
- Comprehensive error handling
- GPU/CPU automatic detection
- Memory optimization
- Singleton pattern for efficient resource usage
"""
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM
from peft import PeftModel
from typing import Union, List, Optional
import os
import re
import traceback


class Florence2VQAService:
    """
    Service for Visual Question Answering using Florence-2
    
    Optimized for satellite image analysis with support for:
    - Binary questions (Yes/No)
    - Numeric questions (counts)
    - Semantic questions (descriptive)
    """
    
    def __init__(
        self,
        model_path: str = "../../checkpoints/vqa_model",
        base_model: str = "microsoft/Florence-2-large",
        device: str = None,
        dtype: torch.dtype = torch.float32
    ):
        """
        Initialize Florence-2 VQA service
        
        Args:
            model_path: Path to LoRA checkpoint (optional, but recommended)
            base_model: Base Florence-2 model name
            device: Device to run on ('cuda', 'cpu', or None for auto)
            dtype: Model data type (default: float32 for compatibility)
        """
        # Device configuration
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = dtype
        
        print(f"[Florence2VQAService] 🚀 Initializing on {self.device}")
        print(f"[Florence2VQAService] Data type: {self.dtype}")
        
        # Load processor
        processor_source = model_path if (model_path and os.path.exists(model_path)) else base_model
        print(f"[Florence2VQAService] 📦 Loading processor from {processor_source}")
        
        try:
            self.processor = AutoProcessor.from_pretrained(
                processor_source,
                trust_remote_code=True
            )
        except Exception as e:
            print(f"[Florence2VQAService] ⚠️  Failed to load processor from {processor_source}, falling back to base model")
            self.processor = AutoProcessor.from_pretrained(
                base_model,
                trust_remote_code=True
            )
        
        # Configure tokenizer
        if getattr(self.processor.tokenizer, "pad_token", None) is None:
            self.processor.tokenizer.pad_token = self.processor.tokenizer.eos_token
        print(f"[Florence2VQAService] ✅ Tokenizer configured (vocab size: {len(self.processor.tokenizer)})")
        
        # Load base model
        print(f"[Florence2VQAService] 🤖 Loading base model: {base_model}")
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                base_model,
                trust_remote_code=True,
                torch_dtype=self.dtype,
                device_map=None,
                low_cpu_mem_usage=False,
                attn_implementation="eager"
            )
            print(f"[Florence2VQAService] ✅ Base model loaded")
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Failed to load base model: {e}")
            raise
        
        # Load LoRA weights if provided
        if model_path and os.path.exists(model_path):
            print(f"[Florence2VQAService] 🎯 Loading LoRA weights from {model_path}")
            try:
                self.model = PeftModel.from_pretrained(
                    self.model,
                    model_path,
                    is_trainable=False
                )
                print("[Florence2VQAService] ✅ LoRA adapter loaded successfully")
                self.using_lora = True
            except Exception as e:
                print(f"[Florence2VQAService] ⚠️  LoRA loading failed: {e}")
                print("[Florence2VQAService] Continuing with base model only")
                self.using_lora = False
        else:
            print("[Florence2VQAService] ℹ️  No LoRA checkpoint provided, using base model")
            self.using_lora = False
        
        # Move to device and set to eval mode
        print(f"[Florence2VQAService] 📍 Moving model to {self.device}...")
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # VQA prompt prefix
        self.vqa_prompt = '<VQA>'
        
        # Statistics
        self.total_questions_processed = 0
        self.total_errors = 0
        
        print("[Florence2VQAService] ✅ Service initialized successfully\n")
    
    def preprocess_image(
        self, 
        image: Union[str, Image.Image],
        max_size: int = 1024
    ) -> Image.Image:
        """
        Load and preprocess image with optional resizing
        
        Args:
            image: Path to image or PIL Image
            max_size: Maximum dimension (resizes if larger)
            
        Returns:
            PIL Image in RGB format
            
        Raises:
            ValueError: If image is invalid
        """
        try:
            # Load image if path provided
            if isinstance(image, str):
                if not os.path.exists(image):
                    raise FileNotFoundError(f"Image file not found: {image}")
                image = Image.open(image)
            
            if not isinstance(image, Image.Image):
                raise ValueError(f"Image must be a file path or PIL Image, got {type(image)}")
            
            # Convert to RGB
            if image.mode != 'RGB':
                original_mode = image.mode
                image = image.convert('RGB')
                # print(f"[Florence2VQAService] Converted image from {original_mode} to RGB")
            
            # Validate dimensions
            width, height = image.size
            if width == 0 or height == 0:
                raise ValueError(f"Invalid image dimensions: {width}x{height}")
            
            # Optional: Resize if too large (helps with memory)
            if max(width, height) > max_size:
                ratio = max_size / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                print(f"[Florence2VQAService] ℹ️  Resized image from {width}x{height} to {new_size}")
            
            return image
            
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Error preprocessing image: {e}")
            raise
    
    def answer_question(
        self,
        image: Union[str, Image.Image],
        question: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        num_beams: int = 1
    ) -> str:
        """
        Answer a single question about an image
        
        Args:
            image: Image path or PIL Image
            question: Question to answer
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0 = greedy, >0 = sampling)
            num_beams: Number of beams for beam search (1 = no beam search)
            
        Returns:
            Generated answer as string
            
        Raises:
            Exception: If inference fails
        """
        try:
            # Preprocess image
            image = self.preprocess_image(image)
            
            # Format prompt
            prompt = f"{self.vqa_prompt}{question}"
            
            # Prepare inputs
            inputs = self.processor(
                text=prompt,
                images=image,
                return_tensors="pt"
            )
            
            # Validate inputs
            for key, value in inputs.items():
                if value is None:
                    raise ValueError(f"Input '{key}' is None")
                if isinstance(value, torch.Tensor) and value.numel() == 0:
                    raise ValueError(f"Input '{key}' is empty tensor")
            
            # Move to device
            inputs = {
                k: v.to(self.device) if isinstance(v, torch.Tensor) else v 
                for k, v in inputs.items()
            }
            
            # Generate answer
            with torch.no_grad():
                generated_ids = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    temperature=temperature if temperature > 0 else 1.0,
                    do_sample=True if temperature > 0 else False,
                    num_beams=num_beams,
                    pad_token_id=self.processor.tokenizer.pad_token_id,
                    eos_token_id=self.processor.tokenizer.eos_token_id,
                    use_cache=False  # Disable KV cache for stability
                )
            
            # Decode answer
            generated_text = self.processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            # Extract answer - handle multiple cases
            answer = generated_text.strip()
            
            # Remove full prompt first
            if prompt in answer:
                answer = answer.replace(prompt, "").strip()
            
            # Remove VQA prefix if still present
            if answer.startswith(self.vqa_prompt):
                answer = answer[len(self.vqa_prompt):].strip()
            
            # Remove question if it appears in answer
            if question in answer:
                answer = answer.replace(question, "").strip()
            
            # Final validation
            if not answer or answer == prompt or answer == question:
                answer = "Unable to generate answer"
                self.total_errors += 1
            else:
                self.total_questions_processed += 1
            
            return answer
            
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Error in answer_question: {e}")
            traceback.print_exc()
            self.total_errors += 1
            raise
    
    def answer_multiple_questions(
        self,
        image: Union[str, Image.Image],
        questions: List[str],
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        verbose: bool = False
    ) -> List[str]:
        """
        Answer multiple questions for a single image (optimized)
        
        This method processes the image once and then answers each question.
        More efficient than calling answer_question multiple times.
        
        Args:
            image: Image path or PIL Image
            questions: List of questions to answer
            max_new_tokens: Maximum tokens to generate per answer
            temperature: Sampling temperature
            verbose: Print detailed progress
            
        Returns:
            List of answers corresponding to each question
        """
        if not questions:
            return []
        
        # Preprocess image once
        try:
            image = self.preprocess_image(image)
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Image preprocessing failed: {e}")
            return ["Error: Image preprocessing failed"] * len(questions)
        
        if verbose:
            print(f"[Florence2VQAService] 🖼️  Processing {len(questions)} questions for image...")
        
        answers = []
        
        # Process each question
        for idx, question in enumerate(questions, 1):
            try:
                # Format prompt
                prompt = f"{self.vqa_prompt}{question}"
                
                # Process image and text together (CRITICAL for Florence-2)
                inputs = self.processor(
                    text=prompt,
                    images=image,
                    return_tensors="pt"
                ).to(self.device)
                
                # Generate answer
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
                
                # Decode answer
                generated_text = self.processor.batch_decode(
                    generated_ids,
                    skip_special_tokens=True
                )[0]
                
                # Extract answer - handle multiple cases
                answer = generated_text.strip()
                
                # Remove full prompt first
                if prompt in answer:
                    answer = answer.replace(prompt, "").strip()
                
                # Remove VQA prefix if still present
                if answer.startswith(self.vqa_prompt):
                    answer = answer[len(self.vqa_prompt):].strip()
                
                # Remove question if it appears in answer
                if question in answer:
                    answer = answer.replace(question, "").strip()
                
                # Final validation
                if not answer or answer == prompt or answer == question:
                    answer = "Unable to generate answer"
                    self.total_errors += 1
                else:
                    self.total_questions_processed += 1
                
                answers.append(answer)
                
                if verbose:
                    print(f"  ✓ Question {idx}/{len(questions)}: '{answer[:50]}...'")
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                print(f"[Florence2VQAService] ❌ Error on question {idx}: {e}")
                answers.append(error_msg)
                self.total_errors += 1
        
        return answers
    
    # =========================================================================
    # ANSWER PARSING AND NORMALIZATION
    # =========================================================================
    
    def parse_numeric_answer(self, answer: str) -> float:
        """
        Parse numeric answer from text response
        
        Extracts the first number found in the answer text.
        
        Args:
            answer: Text answer from model
            
        Returns:
            Numeric value as float (0.0 if no number found)
        """
        try:
            # Remove common text patterns
            answer = answer.lower()
            answer = answer.replace("there are", "").replace("there is", "")
            answer = answer.replace("i see", "").replace("i count", "")
            
            # Extract all numbers (including decimals and negatives)
            numbers = re.findall(r'-?\d+\.?\d*', answer)
            
            if numbers:
                # Try to convert first number
                try:
                    value = float(numbers[0])
                    # Validate range (sanity check)
                    if value < 0:
                        print(f"[Florence2VQAService] ⚠️  Warning: Negative count detected: {value}, using 0")
                        return 0.0
                    if value > 10000:
                        print(f"[Florence2VQAService] ⚠️  Warning: Unusually large count: {value}")
                    return value
                except ValueError:
                    pass
            
            # No valid number found
            print(f"[Florence2VQAService] ⚠️  No number found in answer: '{answer[:50]}...', defaulting to 0")
            return 0.0
            
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Error parsing numeric answer: {e}")
            return 0.0
    
    def normalize_binary_answer(self, answer: str) -> str:
        """
        Normalize binary answer to "Yes" or "No"
        
        Uses heuristics to determine if answer is positive or negative.
        
        Args:
            answer: Text answer from model
            
        Returns:
            "Yes" or "No"
        """
        try:
            answer_lower = answer.lower().strip()
            
            # Positive indicators
            positive_keywords = [
                'yes', 'yeah', 'yep', 'true', 'correct', 
                'present', 'visible', 'exists', 'there is', 'there are',
                'can see', 'i see', 'affirmative', 'indeed'
            ]
            
            # Negative indicators  
            negative_keywords = [
                'no', 'nope', 'false', 'incorrect', 
                'absent', 'not present', 'not visible', 'cannot see',
                'no ', 'there is no', 'there are no', 'negative', 'none'
            ]
            
            # Check for explicit matches
            for keyword in positive_keywords:
                if keyword in answer_lower:
                    return "Yes"
            
            for keyword in negative_keywords:
                if keyword in answer_lower:
                    return "No"
            
            # If answer starts with 'yes' or 'no', use that
            if answer_lower.startswith('yes'):
                return "Yes"
            if answer_lower.startswith('no'):
                return "No"
            
            # Default to "No" if unclear (conservative approach)
            print(f"[Florence2VQAService] ⚠️  Ambiguous binary answer: '{answer[:50]}...', defaulting to 'No'")
            return "No"
            
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Error normalizing binary answer: {e}")
            return "No"
    
    def clean_semantic_answer(self, answer: str) -> str:
        """
        Clean semantic answer text
        
        Removes common artifacts and normalizes whitespace.
        
        Args:
            answer: Raw text answer
            
        Returns:
            Cleaned answer text
        """
        try:
            # Strip whitespace
            answer = answer.strip()
            
            # Remove common prefixes
            prefixes_to_remove = [
                "the answer is ",
                "the color is ",
                "it is ",
                "it's ",
                "i see ",
                "i can see "
            ]
            
            answer_lower = answer.lower()
            for prefix in prefixes_to_remove:
                if answer_lower.startswith(prefix):
                    answer = answer[len(prefix):]
                    break
            
            # Capitalize first letter
            if answer:
                answer = answer[0].upper() + answer[1:]
            
            # Remove trailing periods if present
            if answer.endswith('.'):
                answer = answer[:-1]
            
            return answer
            
        except Exception as e:
            print(f"[Florence2VQAService] ❌ Error cleaning semantic answer: {e}")
            return answer
    
    # =========================================================================
    # RESOURCE MANAGEMENT
    # =========================================================================
    
    def get_statistics(self) -> dict:
        """
        Get service statistics
        
        Returns:
            Dictionary with processing statistics
        """
        return {
            "total_questions_processed": self.total_questions_processed,
            "total_errors": self.total_errors,
            "success_rate": (
                self.total_questions_processed / 
                (self.total_questions_processed + self.total_errors)
                if (self.total_questions_processed + self.total_errors) > 0 
                else 0.0
            ),
            "using_lora": self.using_lora,
            "device": str(self.device)
        }
    
    def cleanup(self):
        """
        Cleanup resources and free memory
        """
        try:
            print(f"[Florence2VQAService] 🧹 Cleaning up resources...")
            
            # Print statistics
            stats = self.get_statistics()
            print(f"[Florence2VQAService] 📊 Statistics:")
            print(f"  Questions processed: {stats['total_questions_processed']}")
            print(f"  Errors: {stats['total_errors']}")
            print(f"  Success rate: {stats['success_rate']:.2%}")
            
            # Delete model and processor
            del self.model
            del self.processor
            
            # Clear CUDA cache if using GPU
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print(f"[Florence2VQAService] ✅ CUDA cache cleared")
            
            print("[Florence2VQAService] ✅ Resources cleaned up successfully")
            
        except Exception as e:
            print(f"[Florence2VQAService] ⚠️  Cleanup error: {e}")


# =============================================================================
# SINGLETON PATTERN
# =============================================================================

# Global service instance
_vqa_service = None


def get_vqa_service(
    model_path: str = None,
    force_reload: bool = False
) -> Florence2VQAService:
    """
    Get or create global VQA service instance (singleton pattern)
    
    This ensures the model is loaded only once and reused across requests,
    which is much more efficient than loading for each request.
    
    Args:
        model_path: Path to LoRA checkpoint
        force_reload: Force reload the service (useful for model updates)
        
    Returns:
        Florence2VQAService instance
    """
    global _vqa_service
    
    if _vqa_service is None or force_reload:
        print("[get_vqa_service] Creating new VQA service instance...")
        _vqa_service = Florence2VQAService(model_path=model_path)
    else:
        print("[get_vqa_service] Using existing VQA service instance")
    
    return _vqa_service


def cleanup_vqa_service():
    """
    Cleanup global VQA service instance
    
    Call this to free resources (e.g., during application shutdown)
    """
    global _vqa_service
    
    if _vqa_service is not None:
        _vqa_service.cleanup()
        _vqa_service = None
        print("[cleanup_vqa_service] ✅ VQA service cleaned up")
    else:
        print("[cleanup_vqa_service] ℹ️  No VQA service to cleanup")