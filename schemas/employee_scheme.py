
def employee_helper(employee) -> dict:
    return {
        "id": str(employee["_id"]),
        "employeeName": employee["employeeName"],
        "email": employee["email"],
        "rol": employee["rol"],
        "createdAt": employee["createdAt"].isoformat() if "createdAt" in employee else None,
    }