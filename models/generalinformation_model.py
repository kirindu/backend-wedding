from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class GeneralInformationModel(BaseModel):
    

    # ✅ GENERAL INFORMATION
    
   
    date: Optional[datetime] = None
    trainerName: Optional[str] = None
    
    employee_id: Optional[str] = None
    truck_id: Optional[str] = None
    dept_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    typeOfIncident_id: Optional[str] = None
    
    location: Optional[str] = None
    time: Optional[str] = None
    timeWorkedYears: Optional[int] = None
    timeWorkedMonths: Optional[int] = None
    timeDayStarted: Optional[str] = None
    
           
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)

    # ✅ Estado de firmas
    signedByEmployee: bool = Field(default=False)
    signedBySupervisor: bool = Field(default=False)
    
    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None  
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None