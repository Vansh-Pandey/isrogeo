from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue
from pydantic import GetJsonSchemaHandler


# --------------------------
# FIXED PyObjectId for V2
# --------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.update(type="string")
        return schema


# --------------------------
# IMAGE MODELS
# --------------------------

class ImageUpload(BaseModel):
    sessionId: str


class ImageAnalyzeRequest(BaseModel):
    sessionId: str
    imageData: str
    prompt: str = Field(..., min_length=1)


class ImageInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    sessionId: str
    userId: str
    filename: str
    filepath: str
    mimetype: str
    size: int
    uploadedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class ImageResponse(BaseModel):
    _id: str
    sessionId: str
    userId: str
    filename: str
    filepath: str
    mimetype: str
    size: int
    uploadedAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "_id": "60f7ff78f7762f1a20d8c4a7",
                    "sessionId": "60f7ff78f7762f1a20d8c4a8",
                    "userId": "60f7ff78f7762f1a20d8c4a9",
                    "filename": "satellite.jpg",
                    "filepath": "/uploads/satellite.jpg",
                    "mimetype": "image/jpeg",
                    "size": 1024000,
                    "uploadedAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
    )


class ImageAnalyzeResponse(BaseModel):
    analysis: str
    messageId: str