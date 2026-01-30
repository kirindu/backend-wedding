from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class LoadModel(BaseModel):
    firstStopTime: Optional[str] = None
    route_id: Optional[str] = None
    lastStopTime: Optional[str] = None
    landFillTimeIn: Optional[str] = None
    landFillTimeOut: Optional[str] = None
    
    # ✅ OPTIMIZADO: Cambiados de str a float
    grossWeight: Optional[float] = None   # ✅ float en lugar de str
    tareWeight: Optional[float] = None    # ✅ float en lugar de str
    tons: Optional[float] = None          # ✅ float en lugar de str
    
    landFill_id: Optional[str] = None
    material_id: Optional[str] = None
    ticketNumber: Optional[str] = None
    note: Optional[str] = None
    
    # 🆕 Nueva referencia al padre coversheet
    coversheet_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None