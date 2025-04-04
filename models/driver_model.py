from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class DriverModel(BaseModel):
    name: str
    email: EmailStr
    rol: str
    password: str
    creationDate: Optional[float] = Field(default_factory=lambda: datetime.timestamp(datetime.now()))

    # class Config:
    #     arbitrary_types_allowed = True
    #     json_encoders = {ObjectId: str}

