from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DuringTheIncidentModel(BaseModel):

    # ✅ DURING THE INCIDENT
    usingElectronicDevice: Optional[bool] = None
    taskPerfomed: Optional[str] = None

    wasSafetyDeptNotified: Optional[bool] = None
    didYouTakePictures: Optional[bool] = None

    howFastWereYouGoing: Optional[int] = None

    # ✅ Nombres alineados con los que envía el frontend
    safetyPersonNotified_id: Optional[str] = None
    whoDidYouSendThePicturesTo_id: Optional[str] = None   # ✅ era whoDidYouSendPicturesTo_id

    directionYouWereTraveling_id: Optional[str] = None
    weatherCondition_id: Optional[str] = None             # ✅ era weatherConditions_id
    roadCondition_id: Optional[str] = None                # ✅ era roadConditions_id

    wasThisIncidentInAnIntersection: Optional[bool] = None
    witness: Optional[str] = None
    witnessPhone: Optional[str] = None

    # Referencia al padre
    generalInformation_ref_id: Optional[str] = None

    # Campo para soft deletes
    active: bool = Field(default=True)

    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    createdAt: Optional[datetime] = None   # ✅ Sin default_factory para evitar bug en PUT
    updatedAt: Optional[datetime] = None