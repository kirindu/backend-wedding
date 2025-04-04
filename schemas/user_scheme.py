
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["nombre"],
        "email": user["email"],
        "rol": user["rol"],
        "password": user["password"],
        "creationDate": user["creationDate"]
    }