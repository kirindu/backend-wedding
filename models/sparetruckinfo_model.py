from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class SpareTruckInfoModel(BaseModel):
    spareTruckNumber: Optional[str] = None
    route_id: Optional[str] = None
    leaveYard: Optional[str] = None
    backInYard: Optional[str] = None
    
    # ✅ OPTIMIZADO: Cambiados de str a int/float
    startMiles: Optional[int] = None  # ✅ int en lugar de str
    endMiles: Optional[int] = None    # ✅ int en lugar de str
    fuel: Optional[float] = None      # ✅ float en lugar de str (para decimales)
    
    # 🆕 Nueva referencia al padre coversheet
    coversheet_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None