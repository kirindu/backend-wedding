from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime, timezone



class DriverModel(BaseModel):
    name: str
    email: EmailStr
    rol: str
    password: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))