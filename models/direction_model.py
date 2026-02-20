from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from datetime import datetime, timezone



class DirectionModel(BaseModel):
    directionName: Optional[str]= None
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))  