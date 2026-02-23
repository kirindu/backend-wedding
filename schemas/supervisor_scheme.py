def supervisor_helper(supervisor) -> dict:
    return {
        "id": str(supervisor["_id"]),
        "supervisorName": supervisor["routeNumber"],
        "lob": supervisor["lob"],
        
        # SOFT DELETE FIELD
        "active": supervisor.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(supervisor["createdBy"]) if supervisor.get("createdBy") else None,
        "updatedBy" : str(supervisor["updatedBy"]) if supervisor.get("updatedBy") else None,
        "createdAt": supervisor["createdAt"].isoformat() if supervisor.get("createdAt") else None,
        "updatedAt": supervisor["updatedAt"].isoformat() if supervisor.get("updatedAt") else None,
        
    }