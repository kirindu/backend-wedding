from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime, timezone



class EmployeeModel(BaseModel):
    employeeName: Optional[str]= None
    email: EmailStr
    rol: str = Field(default="Driver")
    password: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))