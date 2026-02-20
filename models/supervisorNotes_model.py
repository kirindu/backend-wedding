from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class SupervisorNotesModel(BaseModel):

 # ✅ SUPERVISOR NOTES FIELDS
    
    notes: Optional[str] = None
   
    # 🆕 referencia al padre
    generalInformation_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None