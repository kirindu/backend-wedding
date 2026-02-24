def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),

        # ✅ Corregido: usando .get() para evitar KeyError
        "name": user.get("name"),
        "email": user.get("email"),
        "rol": user.get("rol"),

        # SOFT DELETE FIELD
        "active": user.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(user["createdBy"]) if user.get("createdBy") else None,
        "updatedBy": str(user["updatedBy"]) if user.get("updatedBy") else None,
        "createdAt": user["createdAt"].isoformat() if user.get("createdAt") else None,
        "updatedAt": user["updatedAt"].isoformat() if user.get("updatedAt") else None,
    }