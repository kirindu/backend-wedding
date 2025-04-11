
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "rol": user["rol"],
        "password": user["password"],
        "createdAt": user["createdAt"]
    }