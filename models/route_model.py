from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from datetime import datetime, timezone


class RouteModel(BaseModel):
    routeNumber: str
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

