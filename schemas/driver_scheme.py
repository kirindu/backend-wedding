
def driver_helper(driver) -> dict:
    return {
        "id": str(driver["_id"]),
        "name": driver["name"],
        "email": driver["email"],
        "rol": driver["rol"],
        "password": driver["password"],
        "creationDate": driver["creationDate"]
    }