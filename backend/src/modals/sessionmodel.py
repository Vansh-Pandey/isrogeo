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
# SESSION MODELS
# --------------------------

class SessionCreate(BaseModel):
    name: str = Field(default="New Analysis", max_length=200)
    archived: bool = Field(default=False)
    projectId: Optional[str] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    archived: Optional[bool] = None
    projectId: Optional[str] = None


class SessionInDB(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    userId: str
    name: str
    archived: bool = Field(default=False)
    projectId: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=(), 
        arbitrary_types_allowed=True,
    )


class SessionResponse(BaseModel):
    _id: str
    userId: str
    name: str
    archived: bool
    projectId: Optional[str] = None
    createdAt: datetime
    updatedAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        protected_namespaces=(),   
        json_schema_extra={
            "examples": [
                {
                    "_id": "60f7ff78f7762f1a20d8c4a7",
                    "userId": "60f7ff78f7762f1a20d8c4a8",
                    "name": "Analysis Session 1",
                    "archived": False,
                    "projectId": None,
                    "createdAt": "2024-01-01T00:00:00Z",
                    "updatedAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
    )



class ShareSessionResponse(BaseModel):
    shareLink: str