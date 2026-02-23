def employee_signature_helper(employeeSignature) -> dict:
    return {
        "id": str(employeeSignature["_id"]),
        "employeeSignature": employeeSignature["employeeSignature"],
        "date": employeeSignature["date"].isoformat() if employeeSignature.get("date") else None,  
        
         
        # 🆕 referencia al padre
        "generalInformation_ref_id": str(employeeSignature["generalInformation_ref_id"]) if employeeSignature.get("generalInformation_ref_id") else None,     
        
    
 # SOFT DELETE FIELD
        "active": employeeSignature.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(employeeSignature["createdBy"]) if employeeSignature.get("createdBy") else None,
        "updatedBy" : str(employeeSignature["updatedBy"]) if employeeSignature.get("updatedBy") else None,
        "createdAt": employeeSignature["createdAt"].isoformat() if employeeSignature.get("createdAt") else None,
        "updatedAt": employeeSignature["updatedAt"].isoformat() if employeeSignature.get("updatedAt") else None,  
    }