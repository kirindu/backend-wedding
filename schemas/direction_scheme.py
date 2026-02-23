
def direction_helper(direction) -> dict:
    return {
        "id": str(direction["_id"]),
        "directionName": direction["directionName"],
        
        # SOFT DELETE FIELD
        "active": direction.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(direction["createdBy"]) if direction.get("createdBy") else None,
        "updatedBy" : str(direction["updatedBy"]) if direction.get("updatedBy") else None,
        "createdAt": direction["createdAt"].isoformat() if direction.get("createdAt") else None,
        "updatedAt": direction["updatedAt"].isoformat() if direction.get("updatedAt") else None,
    }