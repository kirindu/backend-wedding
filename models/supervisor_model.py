from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class SupervisorModel(BaseModel):
    supervisorName: str
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None  
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None 