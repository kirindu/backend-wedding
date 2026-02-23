from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class IncidentDetailModel(BaseModel):
    
    # ✅ INCIDENT DETAILS
    
    incidentDescription: Optional[str] = None
    actionEventCondition: Optional[str] = None
    wereAnyVehiclesTowed: Optional[bool] = None
    wasAnyOneHurt: Optional[bool] = None
    describeAnyInjuries: Optional[str] = None
    damageToAceTruck: Optional[str] = None
    whatDamageWasDone: Optional[str] = None
    incidentInThePastYear: Optional[bool] = None
    listDatesOfIncidents: Optional[str] = None
    
    images: Optional[list] = []
    image_path: Optional[str] = None
    
    
    # 🆕 referencia al padre
    generalInformation_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None  
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None 