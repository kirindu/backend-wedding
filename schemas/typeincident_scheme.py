
def type_incident_helper(typeincident) -> dict:
    return {
        "id": str(typeincident["_id"]),
        "typeIncidentName": typeincident["typeIncidentName"],
        
        # SOFT DELETE FIELD
        "active": typeincident.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(typeincident["createdBy"]) if typeincident.get("createdBy") else None,
        "updatedBy" : str(typeincident["updatedBy"]) if typeincident.get("updatedBy") else None,
        "createdAt": typeincident["createdAt"].isoformat() if typeincident.get("createdAt") else None,
        "updatedAt": typeincident["updatedAt"].isoformat() if typeincident.get("updatedAt") else None,
        
        
    
    }