from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class SpareTruckInfoModel(BaseModel):
    spareTruckNumber: Optional[str]= None
    route_id: Optional[str]= None
    leaveYard: Optional[str]= None
    backInYard: Optional[str]= None
    startMiles: Optional[str]= None
    endMiles: Optional[str]= None
    fuel: Optional[str]= None
    coversheet_id: Optional[str]= None
    
        # OTHER FIELDS
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None