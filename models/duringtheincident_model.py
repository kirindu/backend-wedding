from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class DuringTheIncidentModel(BaseModel):
    
    
    # ✅ DURING THE INCIDENT
    
    usingElectronicDevice: Optional[bool] = None
    taskPerfomed: Optional[str] = None
    
    
    wasSafetyDeptNotified: Optional[bool] = None
    didYouTakePictures: Optional[bool] = None
    
    
    
    

    
    
    howFastWereYouGoing: Optional[str] = None
    
    safetyPersonNotified_id: Optional[str] = None
    whoDidYouSendPicturesTo_id: Optional[str] = None
    
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
    
    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None  
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None 