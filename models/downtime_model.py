from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime



class DowntimeModel(BaseModel):
    truckNumber: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    downtimeReason: Optional[str] = None
    coversheet_id: Optional[str]= None
 