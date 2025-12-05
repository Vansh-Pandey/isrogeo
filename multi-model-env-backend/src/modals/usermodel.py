from pydantic import BaseModel, EmailStr, Field, ConfigDict
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

    # NEW way of modifying schema in Pydantic v2
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        schema = handler(core_schema)
        schema.update(type="string")
        return schema


# --------------------------
# USER MODELS
# --------------------------

class UserBase(BaseModel):
    email: EmailStr
    fullName: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    password: str
    profilePic: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,  # replaces allow_population_by_field_name
        arbitrary_types_allowed=True,
    )


class UserResponse(BaseModel):
    _id: str
    email: EmailStr
    fullName: str
    profilePic: Optional[str] = None
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "examples": [
                {
                    "_id": "60f7ff78f7762f1a20d8c4a7",
                    "email": "test@example.com",
                    "fullName": "Test User",
                    "profilePic": None,
                    "createdAt": "2024-01-01T00:00:00Z"
                }
            ]
        }
    )


class UpdateProfile(BaseModel):
    fullName: Optional[str] = Field(None, min_length=1, max_length=100)
    profilePic: Optional[str] = None