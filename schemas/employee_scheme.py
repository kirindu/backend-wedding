
def employee_helper(employee) -> dict:
    return {
        "id": str(employee["_id"]),
        "employeeName": employee["employeeName"],
        "email": employee["email"],
        "rol": employee["rol"],
        
        # SOFT DELETE FIELD
        "active": employee.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(employee["createdBy"]) if employee.get("createdBy") else None,
        "updatedBy" : str(employee["updatedBy"]) if employee.get("updatedBy") else None,
        "createdAt": employee["createdAt"].isoformat() if employee.get("createdAt") else None,
        "updatedAt": employee["updatedAt"].isoformat() if employee.get("updatedAt") else None,
    }