
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "rol": user["rol"],
        "createdAt": user["createdAt"].isoformat() if "createdAt" in user else None,
    }