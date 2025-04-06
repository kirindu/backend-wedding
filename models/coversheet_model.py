from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class CoversheetModel(BaseModel):
    truckInfo_clockIn: str
    truckInfo_leaveYard: str
    truckInfo_backInYard: str
    truckInfo_clockOut: str
    truckInfo_startMiles: str
    truckInfo_endMiles: str
    truckInfo_fuel: str
    
    spareTruckInfo_spareTruckNumber: str
    spareTruckInfo_routeNumber: str
    spareTruckInfo_leaveYard: str
    spareTruckInfo_backInYard: str
    spareTruckInfo_startMiles: str
    spareTruckInfo_endMiles: str
    spareTruckInfo_fuel: str
    
    downtime_truckNumber: str
    downtime_startTime: str
    downtime_downtimeReason: str
    
    
    truck_id: str
    route_id: str
    driver_id: str
    
    creationDate: Optional[float] = Field(default_factory=lambda: datetime.timestamp(datetime.now()))

    # class Config:
    #     arbitrary_types_allowed = True
    #     json_encoders = {ObjectId: str}
