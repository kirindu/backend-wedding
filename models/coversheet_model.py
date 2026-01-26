from zoneinfo import ZoneInfo
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId


class CoversheetModel(BaseModel):
    # TRUCK INFO
    clockIn: str  
    leaveYard: str  
    backInYard: str  
    clockOut: str  
    startMiles: str
    endMiles: str
    fuel: str
 
    # SINGLE RELATIONSHIPS
    truck_id: str
    route_id: str
    driver_id: str
    
    # FIELDS
    date: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    notes: Optional[str] = None
    active: bool = Field(default=True)  # For soft deletes
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(ZoneInfo("America/Denver")))
    updatedAt: Optional[datetime] = None