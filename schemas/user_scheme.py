
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "rol": user["rol"],
        
        # SOFT DELETE FIELD
        "active": user.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(user["createdBy"]) if user.get("createdBy") else None,
        "updatedBy" : str(user["updatedBy"]) if user.get("updatedBy") else None,
        "createdAt": user["createdAt"].isoformat() if user.get("createdAt") else None,
        "updatedAt": user["updatedAt"].isoformat() if user.get("updatedAt") else None,
    }