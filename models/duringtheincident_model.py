from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class DuringTheIncidentModel(BaseModel):
    
    
    # ✅ DURING THE INCIDENT
    
    usingElectronicDevice: Optional[bool] = None
    taskPerfomed: Optional[str] = None
    whereWereYouComingFrom: Optional[str] = None
    whereWereYouGoingTo: Optional[str] = None
    howFastWereYouGoing: Optional[str] = None
    
    directionYouWereTraveling_id: Optional[str] = None
    weatherConditions_id: Optional[str] = None
    roadConditions_id: Optional[str] = None
    
    wasThisIncidentInAnIntersection: Optional[bool] = None
    witness: Optional[str] = None
    witnessPhone: Optional[str] = None
    
    

    # 🆕 referencia al padre
    generalInformation_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None