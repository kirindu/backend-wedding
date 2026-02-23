def supervisor_note_helper(supervisornote) -> dict:
    return {
        "id": str(supervisornote["_id"]),
        "supervisorNote": supervisornote["routeNumber"],
        
        # 🆕 referencia al padre
        "generalInformation_ref_id": str(supervisornote["generalInformation_ref_id"]) if supervisornote.get("generalInformation_ref_id") else None,     
        

        # SOFT DELETE FIELD
        "active": supervisornote.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(supervisornote["createdBy"]) if supervisornote.get("createdBy") else None,
        "updatedBy" : str(supervisornote["updatedBy"]) if supervisornote.get("updatedBy") else None,
        "createdAt": supervisornote["createdAt"].isoformat() if supervisornote.get("createdAt") else None,
        "updatedAt": supervisornote["updatedAt"].isoformat() if supervisornote.get("updatedAt") else None,
        
    }