from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SupervisorNoteModel(BaseModel):

 # ✅ SUPERVISOR NOTES FIELDS
    
    supervisorNote: Optional[str] = None
    supervisorSignature: Optional[str] = None
   
    # 🆕 referencia al padre
    generalInformation_ref_id: Optional[str] = None
    
    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # AUDIT FIELDS
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None  
    createdAt: Optional[datetime] = None   # ✅ Sin default_factory para evitar bug en PUT
    updatedAt: Optional[datetime] = None