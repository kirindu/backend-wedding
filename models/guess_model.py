from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GuessModel(BaseModel):

 # ✅ SUPERVISOR NOTES FIELDS
    
    nombre: Optional[str] = None
    cantidadAdultos: Optional[str] = None
    cantidadNinos: Optional[str] = None
    comentarios: Optional[str] = None
   

    # 🆕 Campo para soft deletes
    active: bool = Field(default=True)
    
    # AUDIT FIELDS
    createdAt: Optional[datetime] = None   # ✅ Sin default_factory para evitar bug en PUT
    updatedAt: Optional[datetime] = None