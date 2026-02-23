def dept_helper(dept) -> dict:
    return {
        "id": str(dept["_id"]),
        "deptName": dept["deptName"],
         
         # SOFT DELETE FIELD
        "active": dept.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(dept["createdBy"]) if dept.get("createdBy") else None,
        "updatedBy" : str(dept["updatedBy"]) if dept.get("updatedBy") else None,
        "createdAt": dept["createdAt"].isoformat() if dept.get("createdAt") else None,
        "updatedAt": dept["updatedAt"].isoformat() if dept.get("updatedAt") else None,

    }