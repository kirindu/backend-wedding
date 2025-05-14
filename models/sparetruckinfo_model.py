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
    startMiles: Optional[float]= None
    endMiles: Optional[float]= None
    fuel: Optional[float]= None
    coversheet_id: Optional[str]= None