from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any


# ========================
# INPUT MODELS
# ========================

class ImageMetadata(BaseModel):
    """Metadata for input image"""
    width: int
    height: int
    spatial_resolution_m: float


class InputImage(BaseModel):
    """Input image specification"""
    image_id: str
    image_url: str
    metadata: ImageMetadata


class CaptionQuery(BaseModel):
    """Caption generation query"""
    instruction: str


class GroundingQuery(BaseModel):
    """Object grounding query"""
    instruction: str


class BinaryAttributeQuery(BaseModel):
    """Binary (Yes/No) attribute query"""
    instruction: str


class NumericAttributeQuery(BaseModel):
    """Numeric count query"""
    instruction: str


class SemanticAttributeQuery(BaseModel):
    """Semantic/descriptive query"""
    instruction: str


class AttributeQuery(BaseModel):
    """Collection of attribute queries"""
    binary: Optional[BinaryAttributeQuery] = None
    numeric: Optional[NumericAttributeQuery] = None
    semantic: Optional[SemanticAttributeQuery] = None


class Queries(BaseModel):
    """All query types"""
    caption_query: Optional[CaptionQuery] = None
    grounding_query: Optional[GroundingQuery] = None
    attribute_query: Optional[AttributeQuery] = None


class GeoNLIEvalRequest(BaseModel):
    """Complete GeoNLI evaluation request"""
    input_image: InputImage
    queries: Queries

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
                        "instruction": "Locate and return oriented bounding boxes..."
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
        }
    )


# ========================
# OUTPUT MODELS
# ========================

class OrientedBoundingBox(BaseModel):
    """Oriented bounding box representation"""
    object_id: str = Field(alias="object-id")
    obbox: List[float] = Field(
        ...,
        description="[cx, cy, w, h, angle] normalized to [0,1] except angle in degrees"
    )

    model_config = ConfigDict(populate_by_name=True)


class CaptionResponse(BaseModel):
    """Caption query response"""
    instruction: str
    response: str


class GroundingResponse(BaseModel):
    """Grounding query response"""
    instruction: str
    response: List[OrientedBoundingBox]


class BinaryAttributeResponse(BaseModel):
    """Binary attribute response"""
    instruction: str
    response: str  # "Yes" or "No"


class NumericAttributeResponse(BaseModel):
    """Numeric attribute response"""
    instruction: str
    response: float


class SemanticAttributeResponse(BaseModel):
    """Semantic attribute response"""
    instruction: str
    response: str


class AttributeQueryResponse(BaseModel):
    """Collection of attribute query responses"""
    binary: Optional[BinaryAttributeResponse] = None
    numeric: Optional[NumericAttributeResponse] = None
    semantic: Optional[SemanticAttributeResponse] = None


class QueryResponses(BaseModel):
    """All query responses"""
    caption_query: Optional[CaptionResponse] = None
    grounding_query: Optional[GroundingResponse] = None
    attribute_query: Optional[AttributeQueryResponse] = None


class GeoNLIEvalResponse(BaseModel):
    """Complete GeoNLI evaluation response"""
    input_image: InputImage
    queries: QueryResponses

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
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
                            "instruction": "Is there any digit?",
                            "response": "Yes"
                        },
                        "numeric": {
                            "instruction": "How many tanks?",
                            "response": 2.0
                        },
                        "semantic": {
                            "instruction": "What color?",
                            "response": "White"
                        }
                    }
                }
            }
        }
    )