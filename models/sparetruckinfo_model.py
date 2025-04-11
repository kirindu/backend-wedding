from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class SpareTruckInfoModel(BaseModel):
    spareTruckNumber: Optional[str]= None
    routeNumber: Optional[str]= None
    leaveYard: Optional[str]= None
    backInYard: Optional[str]= None
    startMiles: Optional[str]= None
    endMiles: Optional[str]= None
    fuel: Optional[str]= None