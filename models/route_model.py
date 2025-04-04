from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class RouteModel(BaseModel):
    routeNumber: str
    creationDate: Optional[float] = Field(default_factory=lambda: datetime.timestamp(datetime.now()))
    
    
    # class Config:
    #     arbitrary_types_allowed = True
    #     json_encoders = {ObjectId: str}


