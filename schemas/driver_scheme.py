
def driver_helper(driver) -> dict:
    return {
        "id": str(driver["_id"]),
        "name": driver["name"],
        "email": driver["email"],
        "rol": driver["rol"],
        "createdAt": driver["createdAt"].isoformat() if "createdAt" in driver else None,
    }