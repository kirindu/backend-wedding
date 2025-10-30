from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class LoadModel(BaseModel):
    firstStopTime: Optional[str]= None
    route_id: Optional[str]= None
    lastStopTime: Optional[str]= None
    landFillTimeIn: Optional[str]= None
    landFillTimeOut: Optional[str]= None
    grossWeight: Optional[float]= None
    tareWeight: Optional[float]= None
    tons: Optional[float]= None
    landFill_id: Optional[str]= None
    material_id: Optional[str]= None
    ticketNumber: Optional[str]= None
    note: Optional[str]= None
    
 