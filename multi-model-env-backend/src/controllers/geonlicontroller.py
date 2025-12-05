"""
GeoNLI Evaluation Controller
Handles GeoNLI evaluation API requests

This controller orchestrates the complete evaluation pipeline:
1. Downloads and validates input images
2. Routes queries to appropriate AI services
3. Aggregates and formats results
4. Handles errors gracefully with fallbacks
"""
from fastapi import HTTPException, status
from src.models.geonlimodel import (
    GeoNLIEvalRequest,
    GeoNLIEvalResponse,
    QueryResponses,
    CaptionResponse,
    GroundingResponse,
    AttributeQueryResponse,
    BinaryAttributeResponse,
    NumericAttributeResponse,
    SemanticAttributeResponse,
    OrientedBoundingBox
)
from src.services import get_caption_service, get_vqa_service, get_grounding_service
from src.utils.image_utils import download_image, save_temp_image, cleanup_temp_image, validate_image_dimensions
import os
import traceback
from typing import Optional
from datetime import datetime


# Model paths configuration from environment variables
CAPTION_MODEL_PATH = os.getenv("CAPTION_MODEL_PATH", None)
VQA_MODEL_PATH = os.getenv("VQA_MODEL_PATH", None)
GROUNDING_MODEL_PATH = os.getenv("GROUNDING_MODEL_PATH", None)
GROUNDING_MODEL_BASE = os.getenv("GROUNDING_MODEL_BASE", None)

# Grounding configuration
GROUNDING_CONV_MODE = os.getenv("GROUNDING_CONV_MODE", "llava_v1")
GROUNDING_MAX_BOXES = int(os.getenv("GROUNDING_MAX_BOXES", "10"))

# Performance configuration
MAX_CAPTION_TOKENS = int(os.getenv("MAX_CAPTION_TOKENS", "512"))
MAX_VQA_TOKENS = int(os.getenv("MAX_VQA_TOKENS", "128"))
CAPTION_TEMPERATURE = float(os.getenv("CAPTION_TEMPERATURE", "0.7"))
VQA_TEMPERATURE = float(os.getenv("VQA_TEMPERATURE", "0.7"))
IMAGE_DOWNLOAD_TIMEOUT = int(os.getenv("IMAGE_DOWNLOAD_TIMEOUT", "30"))



async def evaluate_geonli(eval_request: GeoNLIEvalRequest) -> GeoNLIEvalResponse:
    """
    Process GeoNLI evaluation request
    
    This is the main entry point for GeoNLI evaluation. It orchestrates:
    1. Image acquisition and validation
    2. Query processing across multiple AI services
    3. Result aggregation and formatting
    4. Error handling and cleanup
    
    Args:
        eval_request: GeoNLI evaluation request with image and queries
        
    Returns:
        GeoNLIEvalResponse with all query results
        
    Raises:
        HTTPException: If processing fails critically
    """
    start_time = datetime.now()
    temp_image_path = None
    
    # Log request details
    _log_request_start(eval_request)
    
    try:
        # ===================================================================
        # STEP 1: IMAGE ACQUISITION AND VALIDATION
        # ===================================================================
        print("\n[STEP 1/5] 📥 Downloading and validating image...")
        
        try:
            image = download_image(
                eval_request.input_image.image_url,
                timeout=IMAGE_DOWNLOAD_TIMEOUT
            )
            print(f"  ✅ Image downloaded: {image.size[0]}x{image.size[1]}")
        except Exception as e:
            error_msg = f"Failed to download image from {eval_request.input_image.image_url}"
            print(f"  ❌ {error_msg}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{error_msg}. Please verify the URL is accessible."
            )
        
        # Validate image dimensions
        expected_width = eval_request.input_image.metadata.width
        expected_height = eval_request.input_image.metadata.height
        actual_width, actual_height = image.size
        
        if not validate_image_dimensions(image, expected_width, expected_height):
            print(f"  ⚠️  Warning: Dimension mismatch!")
            print(f"      Expected: {expected_width}x{expected_height}")
            print(f"      Actual:   {actual_width}x{actual_height}")
            # Note: We proceed with warning, not error
        else:
            print(f"  ✅ Dimensions validated: {actual_width}x{actual_height}")
        
        # Save to temporary file for model processing
        try:
            temp_image_path = save_temp_image(image, eval_request.input_image.image_id)
            print(f"  ✅ Image saved to: {temp_image_path}")
        except Exception as e:
            print(f"  ❌ Failed to save temporary image: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process image file."
            )
        
        # ===================================================================
        # STEP 2: INITIALIZE RESPONSE STRUCTURE
        # ===================================================================
        print("\n[STEP 2/5] 🏗️  Initializing response structure...")
        response_queries = QueryResponses()
        query_count = 0
        
        if eval_request.queries.caption_query:
            query_count += 1
        if eval_request.queries.grounding_query:
            query_count += 1
        if eval_request.queries.attribute_query:
            if eval_request.queries.attribute_query.binary:
                query_count += 1
            if eval_request.queries.attribute_query.numeric:
                query_count += 1
            if eval_request.queries.attribute_query.semantic:
                query_count += 1
        
        print(f"  ✅ Processing {query_count} total queries")
        
        # ===================================================================
        # STEP 3: PROCESS CAPTION QUERY
        # ===================================================================
        if eval_request.queries.caption_query:
            print("\n[STEP 3/5] 📝 Processing caption query...")
            response_queries.caption_query = await _process_caption_query(
                temp_image_path,
                eval_request.queries.caption_query.instruction
            )
            if response_queries.caption_query:
                caption_preview = response_queries.caption_query.response[:100]
                print(f"  ✅ Caption generated: {caption_preview}...")
            else:
                print(f"  ⚠️  Caption generation returned empty result")
        else:
            print("\n[STEP 3/5] ⏭️  Skipping caption query (not requested)")
        
        # ===================================================================
        # STEP 4: PROCESS GROUNDING QUERY
        # ===================================================================
        if eval_request.queries.grounding_query:
            print("\n[STEP 4/5] 🎯 Processing grounding query...")
            response_queries.grounding_query = await _process_grounding_query(
                temp_image_path,
                eval_request.queries.grounding_query.instruction
            )
            if response_queries.grounding_query:
                obj_count = len(response_queries.grounding_query.response)
                print(f"  ✅ Detected {obj_count} objects")
                for idx, bbox in enumerate(response_queries.grounding_query.response[:3], 1):
                    print(f"      Object {bbox.object_id}: {bbox.obbox}")
                if obj_count > 3:
                    print(f"      ... and {obj_count - 3} more")
            else:
                print(f"  ⚠️  Grounding returned no objects")
        else:
            print("\n[STEP 4/5] ⏭️  Skipping grounding query (not requested)")
        
        # ===================================================================
        # STEP 5: PROCESS ATTRIBUTE QUERIES
        # ===================================================================
        if eval_request.queries.attribute_query:
            print("\n[STEP 5/5] ❓ Processing attribute queries...")
            response_queries.attribute_query = await _process_attribute_queries(
                temp_image_path,
                eval_request.queries.attribute_query
            )
            
            if response_queries.attribute_query:
                if response_queries.attribute_query.binary:
                    print(f"  ✅ Binary: {response_queries.attribute_query.binary.response}")
                if response_queries.attribute_query.numeric:
                    print(f"  ✅ Numeric: {response_queries.attribute_query.numeric.response}")
                if response_queries.attribute_query.semantic:
                    semantic_preview = response_queries.attribute_query.semantic.response[:50]
                    print(f"  ✅ Semantic: {semantic_preview}...")
        else:
            print("\n[STEP 5/5] ⏭️  Skipping attribute queries (not requested)")
        
        # ===================================================================
        # BUILD FINAL RESPONSE
        # ===================================================================
        print("\n[FINAL] 🎁 Building response...")
        response = GeoNLIEvalResponse(
            input_image=eval_request.input_image,
            queries=response_queries
        )
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        print("\n" + "="*70)
        print("✅ EVALUATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print(f"  Image ID: {eval_request.input_image.image_id}")
        print(f"  Queries processed: {query_count}")
        print(f"  Processing time: {processing_time:.2f}s")
        print("="*70 + "\n")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is (already formatted)
        raise
        
    except Exception as e:
        # Catch any unexpected errors
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"GeoNLI evaluation failed: {str(e)}"
        )
    
    finally:
        # ===================================================================
        # CLEANUP
        # ===================================================================
        if temp_image_path:
            try:
                cleanup_temp_image(temp_image_path)
                print(f"🧹 Cleaned up temporary image: {temp_image_path}")
            except Exception as e:
                print(f"⚠️  Warning: Failed to cleanup temp image: {e}")


def _log_request_start(eval_request: GeoNLIEvalRequest):
    """Log the start of a GeoNLI evaluation request"""
    print("\n" + "="*70)
    print("🚀 GEONLI EVALUATION REQUEST")
    print("="*70)
    print(f"  Image ID:    {eval_request.input_image.image_id}")
    print(f"  Image URL:   {eval_request.input_image.image_url}")
    print(f"  Dimensions:  {eval_request.input_image.metadata.width}x{eval_request.input_image.metadata.height}")
    print(f"  Resolution:  {eval_request.input_image.metadata.spatial_resolution_m}m")
    print(f"  Timestamp:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    queries = []
    if eval_request.queries.caption_query:
        queries.append("Caption")
    if eval_request.queries.grounding_query:
        queries.append("Grounding")
    if eval_request.queries.attribute_query:
        attr_queries = []
        if eval_request.queries.attribute_query.binary:
            attr_queries.append("Binary")
        if eval_request.queries.attribute_query.numeric:
            attr_queries.append("Numeric")
        if eval_request.queries.attribute_query.semantic:
            attr_queries.append("Semantic")
        if attr_queries:
            queries.append(f"Attribute ({', '.join(attr_queries)})")
    
    print(f"  Queries:     {', '.join(queries) if queries else 'None'}")
    print("="*70)


async def _process_caption_query(
    image_path: str,
    instruction: str
) -> CaptionResponse:
    """
    Process caption generation query
    
    Generates a detailed caption describing all visible elements in the image.
    Uses Florence-2 model with <MORE_DETAILED_CAPTION> task.
    
    Args:
        image_path: Path to image file
        instruction: Caption instruction (for reference, not used by model)
        
    Returns:
        CaptionResponse with generated caption
    """
    try:
        print(f"  📝 Initializing caption service...")
        
        # Get caption service (singleton pattern)
        caption_service = get_caption_service(model_path=CAPTION_MODEL_PATH)
        
        print(f"  🎨 Generating caption (max_tokens={MAX_CAPTION_TOKENS})...")
        
        # Generate caption
        caption = caption_service.generate_caption(
            image=image_path,
            max_new_tokens=MAX_CAPTION_TOKENS,
            temperature=CAPTION_TEMPERATURE
        )
        
        # Validate output
        if not caption or len(caption.strip()) == 0:
            print(f"  ⚠️  Warning: Empty caption generated, using fallback")
            caption = "Unable to generate a detailed caption for this image."
        
        print(f"  ✅ Caption length: {len(caption)} characters")
        
        return CaptionResponse(
            instruction=instruction,
            response=caption
        )
        
    except Exception as e:
        print(f"  ❌ Caption generation error: {e}")
        traceback.print_exc()
        
        # Return fallback caption
        fallback_caption = (
            "Unable to generate caption due to processing error. "
            "The image was received but caption generation failed."
        )
        
        return CaptionResponse(
            instruction=instruction,
            response=fallback_caption
        )


async def _process_grounding_query(
    image_path: str,
    instruction: str
) -> GroundingResponse:
    """
    Process object grounding query
    
    Detects objects mentioned in the natural language query and returns
    oriented bounding boxes in the format [cx, cy, w, h, angle].
    
    Args:
        image_path: Path to image file
        instruction: Natural language query describing objects to detect
        
    Returns:
        GroundingResponse with oriented bounding boxes
    """
    try:
        print(f"  🎯 Initializing grounding service...")
        
        # Prepare GeoGround configuration
        grounding_config = {
            'conv_mode': GROUNDING_CONV_MODE
        }
        
        # Get grounding service (singleton pattern)
        grounding_service = get_grounding_service(
            model_path=GROUNDING_MODEL_PATH,
            model_base=GROUNDING_MODEL_BASE,
            config=grounding_config
        )
        
        print(f"  🔍 Detecting objects: '{instruction[:50]}...'")
        
        # Detect objects
        detections = grounding_service.detect_objects(
            image=image_path,
            query=instruction,
            max_boxes=GROUNDING_MAX_BOXES
        )
        
        # Validate detections format
        if not isinstance(detections, list):
            print(f"  ⚠️  Warning: Grounding returned invalid format, expected list")
            detections = []
        
        print(f"  📊 Raw detections: {len(detections)} objects")
        
        # Convert to response format
        bboxes = []
        for obj_id, obbox in detections:
            # Validate obbox format
            if not isinstance(obbox, (list, tuple)) or len(obbox) != 5:
                print(f"  ⚠️  Warning: Invalid bbox format for object {obj_id}: {obbox}")
                continue
            
            # Validate bbox values
            try:
                cx, cy, w, h, angle = obbox
                
                # Ensure coordinates are in [0, 1] range
                if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                    print(f"  ⚠️  Warning: Bbox coordinates out of range for object {obj_id}")
                    # Clip to valid range
                    cx = max(0, min(1, cx))
                    cy = max(0, min(1, cy))
                    w = max(0, min(1, w))
                    h = max(0, min(1, h))
                
                bboxes.append(
                    OrientedBoundingBox(
                        object_id=str(obj_id),
                        obbox=[float(cx), float(cy), float(w), float(h), float(angle)]
                    )
                )
                
            except (ValueError, TypeError) as e:
                print(f"  ⚠️  Warning: Failed to parse bbox for object {obj_id}: {e}")
                continue
        
        print(f"  ✅ Valid bboxes: {len(bboxes)}/{len(detections)}")
        
        return GroundingResponse(
            instruction=instruction,
            response=bboxes
        )
        
    except Exception as e:
        print(f"  ❌ Grounding error: {e}")
        traceback.print_exc()
        
        # Return empty detections on error
        return GroundingResponse(
            instruction=instruction,
            response=[]
        )


async def _process_attribute_queries(
    image_path: str,
    attribute_query
) -> AttributeQueryResponse:
    """
    Process attribute queries (binary, numeric, semantic)
    
    Uses Florence-2 VQA model to answer various types of questions about the image:
    - Binary: Yes/No questions
    - Numeric: Counting questions
    - Semantic: Descriptive questions
    
    Optimized for batch processing - all questions are processed together.
    
    Args:
        image_path: Path to image file
        attribute_query: AttributeQuery object with binary/numeric/semantic queries
        
    Returns:
        AttributeQueryResponse with all attribute answers
    """
    try:
        print(f"  ❓ Initializing VQA service...")
        
        # Get VQA service (singleton pattern)
        vqa_service = get_vqa_service(model_path=VQA_MODEL_PATH)
        
        response = AttributeQueryResponse()
        
        # ===============================================================
        # COLLECT ALL QUESTIONS FOR BATCH PROCESSING
        # ===============================================================
        questions = []
        question_types = []
        question_instructions = {}
        
        if attribute_query.binary:
            questions.append(attribute_query.binary.instruction)
            question_types.append('binary')
            question_instructions['binary'] = attribute_query.binary.instruction
            print(f"    • Binary: '{attribute_query.binary.instruction[:50]}...'")
        
        if attribute_query.numeric:
            questions.append(attribute_query.numeric.instruction)
            question_types.append('numeric')
            question_instructions['numeric'] = attribute_query.numeric.instruction
            print(f"    • Numeric: '{attribute_query.numeric.instruction[:50]}...'")
        
        if attribute_query.semantic:
            questions.append(attribute_query.semantic.instruction)
            question_types.append('semantic')
            question_instructions['semantic'] = attribute_query.semantic.instruction
            print(f"    • Semantic: '{attribute_query.semantic.instruction[:50]}...'")
        
        if not questions:
            print(f"  ⚠️  No attribute questions provided")
            return response
        
        print(f"  🤖 Processing {len(questions)} questions in batch...")
        
        # ===============================================================
        # ANSWER ALL QUESTIONS AT ONCE (OPTIMIZED)
        # ===============================================================
        try:
            answers = vqa_service.answer_multiple_questions(
                image=image_path,
                questions=questions,
                max_new_tokens=MAX_VQA_TOKENS,
                temperature=VQA_TEMPERATURE
            )
            
            if not answers or len(answers) != len(questions):
                print(f"  ⚠️  VQA returned unexpected number of answers: {len(answers) if answers else 0}/{len(questions)}")
                # Pad with error messages if needed
                answers = answers or []
                while len(answers) < len(questions):
                    answers.append("Unable to generate answer")
            
        except Exception as e:
            print(f"  ❌ VQA batch processing failed: {e}")
            traceback.print_exc()
            # Return error answers for all questions
            answers = ["Error: Unable to process question"] * len(questions)
        
        # ===============================================================
        # PARSE ANSWERS ACCORDING TO TYPE
        # ===============================================================
        print(f"  📝 Parsing {len(answers)} answers...")
        
        for q_type, answer in zip(question_types, answers):
            try:
                if q_type == 'binary':
                    # Normalize to "Yes" or "No"
                    normalized_answer = vqa_service.normalize_binary_answer(answer)
                    response.binary = BinaryAttributeResponse(
                        instruction=question_instructions['binary'],
                        response=normalized_answer
                    )
                    print(f"    ✅ Binary: {normalized_answer} (raw: '{answer[:30]}...')")
                
                elif q_type == 'numeric':
                    # Extract numeric value
                    numeric_answer = vqa_service.parse_numeric_answer(answer)
                    response.numeric = NumericAttributeResponse(
                        instruction=question_instructions['numeric'],
                        response=numeric_answer
                    )
                    print(f"    ✅ Numeric: {numeric_answer} (raw: '{answer[:30]}...')")
                
                elif q_type == 'semantic':
                    # Use answer as-is
                    # Clean up common issues
                    cleaned_answer = answer.strip()
                    if not cleaned_answer:
                        cleaned_answer = "Unable to determine"
                    
                    response.semantic = SemanticAttributeResponse(
                        instruction=question_instructions['semantic'],
                        response=cleaned_answer
                    )
                    print(f"    ✅ Semantic: '{cleaned_answer[:50]}...'")
                    
            except Exception as e:
                print(f"    ⚠️  Warning: Failed to parse {q_type} answer: {e}")
                # Set default/error value
                if q_type == 'binary':
                    response.binary = BinaryAttributeResponse(
                        instruction=question_instructions['binary'],
                        response="No"
                    )
                elif q_type == 'numeric':
                    response.numeric = NumericAttributeResponse(
                        instruction=question_instructions['numeric'],
                        response=0.0
                    )
                elif q_type == 'semantic':
                    response.semantic = SemanticAttributeResponse(
                        instruction=question_instructions['semantic'],
                        response="Unable to determine"
                    )
        
        return response
        
    except Exception as e:
        print(f"  ❌ Attribute query processing failed: {e}")
        traceback.print_exc()
        
        # ===============================================================
        # RETURN DEFAULT/ERROR RESPONSES
        # ===============================================================
        response = AttributeQueryResponse()
        
        if attribute_query.binary:
            response.binary = BinaryAttributeResponse(
                instruction=attribute_query.binary.instruction,
                response="No"
            )
            print(f"    ⚠️  Binary fallback: No")
        
        if attribute_query.numeric:
            response.numeric = NumericAttributeResponse(
                instruction=attribute_query.numeric.instruction,
                response=0.0
            )
            print(f"    ⚠️  Numeric fallback: 0.0")
        
        if attribute_query.semantic:
            response.semantic = SemanticAttributeResponse(
                instruction=attribute_query.semantic.instruction,
                response="Unable to determine due to processing error"
            )
            print(f"    ⚠️  Semantic fallback: Unable to determine")
        
        return response
