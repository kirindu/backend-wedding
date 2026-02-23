
def truck_helper(truck) -> dict:
    return {
        "id": str(truck["_id"]),
        "truckNumber": truck["truckNumber"],
        
        # SOFT DELETE FIELD
        "active": truck.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(truck["createdBy"]) if truck.get("createdBy") else None,
        "updatedBy" : str(truck["updatedBy"]) if truck.get("updatedBy") else None,
        "createdAt": truck["createdAt"].isoformat() if truck.get("createdAt") else None,
        "updatedAt": truck["updatedAt"].isoformat() if truck.get("updatedAt") else None,
        
        
        
    
    }