"""
GeoNLI Evaluation Routes
API endpoints for GeoNLI chat evaluation
"""
from fastapi import APIRouter, HTTPException, status
from src.models.geonlimodel import GeoNLIEvalRequest, GeoNLIEvalResponse
from src.controllers import geonlicontroller


router = APIRouter(prefix="/geoNLI", tags=["GeoNLI Evaluation"])


@router.post(
    "/eval",
    response_model=GeoNLIEvalResponse,
    status_code=200,
    summary="GeoNLI Chat Evaluation",
    description="""
    Process GeoNLI evaluation request for satellite image analysis.
    
    Supports:
    - Caption generation (detailed scene description)
    - Object grounding (oriented bounding boxes)
    - Attribute queries (binary, numeric, semantic)
    
    All queries are optional. The API will process only the queries provided in the request.
    """
)
async def evaluate_geonli(request: GeoNLIEvalRequest):
    """
    GeoNLI Chat Evaluation Endpoint
    
    Request Body:
        - input_image: Image specification with URL and metadata
        - queries: Collection of queries to process
            - caption_query (optional): Caption generation instruction
            - grounding_query (optional): Object detection instruction
            - attribute_query (optional): Attribute questions
                - binary (optional): Yes/No question
                - numeric (optional): Count question
                - semantic (optional): Descriptive question
    
    Returns:
        Complete evaluation response with all query results in JSON format
    
    Example Request:
    ```json
    {
      "input_image": {
        "image_id": "sample1.png",
        "image_url": "https://bit.ly/4ouV45l",
        "metadata": {
          "width": 512,
          "height": 512,
          "spatial_resolution_m": 1.57
        }
      },
      "queries": {
        "caption_query": {
          "instruction": "Generate a detailed caption..."
        },
        "grounding_query": {
          "instruction": "Locate aircrafts..."
        },
        "attribute_query": {
          "binary": {
            "instruction": "Is there any digit present?"
          },
          "numeric": {
            "instruction": "How many storage tanks?"
          },
          "semantic": {
            "instruction": "What is the color of the digit?"
          }
        }
      }
    }
    ```
    
    Example Response:
    ```json
    {
      "input_image": { ... },
      "queries": {
        "caption_query": {
          "instruction": "Generate a detailed caption...",
          "response": "The scene shows an airport runway..."
        },
        "grounding_query": {
          "instruction": "Locate aircrafts...",
          "response": [
            {
              "object-id": "1",
              "obbox": [0.5, 0.17, 0.08, 0.08, -37.18]
            }
          ]
        },
        "attribute_query": {
          "binary": {
            "instruction": "Is there any digit present?",
            "response": "Yes"
          },
          "numeric": {
            "instruction": "How many storage tanks?",
            "response": 2.0
          },
          "semantic": {
            "instruction": "What is the color?",
            "response": "White"
          }
        }
      }
    }
    ```
    """
    try:
        result = await geonlicontroller.evaluate_geonli(request)
        return result
    
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    
    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error in evaluate_geonli route: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if GeoNLI evaluation service is running"
)
async def health_check():
    """
    Health check endpoint for GeoNLI service
    
    Returns:
        Status message indicating service health
    """
    return {
        "status": "healthy",
        "service": "GeoNLI Evaluation",
        "version": "1.0.0"
    }


@router.get(
    "/models/status",
    summary="Model Status",
    description="Check status of loaded AI models"
)
async def model_status():
    """
    Check which AI models are currently loaded
    
    Returns:
        Status of each model service
    """
    from services import get_caption_service, get_vqa_service, get_grounding_service
    
    status_info = {
        "caption_service": "not_loaded",
        "vqa_service": "not_loaded",
        "grounding_service": "not_loaded"
    }
    
    try:
        # Check if services are initialized
        # Note: This doesn't actually load them, just checks if they exist
        from services.florence2_caption_service import _caption_service
        from services.florence2_vqa_service import _vqa_service
        from services.grounding_service import _grounding_service
        
        if _caption_service is not None:
            status_info["caption_service"] = "loaded"
        
        if _vqa_service is not None:
            status_info["vqa_service"] = "loaded"
        
        if _grounding_service is not None:
            status_info["grounding_service"] = "loaded"
    
    except Exception as e:
        print(f"Error checking model status: {e}")
    
    return status_info