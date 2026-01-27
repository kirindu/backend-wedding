from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class DowntimeModel(BaseModel):
    truckNumber: Optional[str] = None
    truck_id: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    downtimeReason: Optional[str] = None
    
    # 🆕 Nueva referencia al padre (antes era coversheet_id)
    coversheet_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None