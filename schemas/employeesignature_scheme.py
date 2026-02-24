def employee_signature_helper(employeeSignature) -> dict:
    return {
        "id": str(employeeSignature["_id"]),

        # ✅ Corregido: date es Optional[str] en el modelo, no datetime — no usar .isoformat()
        "employeeSignature": employeeSignature.get("employeeSignature"),
        "date": employeeSignature.get("date"),

        # Referencia al padre
        "generalInformation_ref_id": str(employeeSignature["generalInformation_ref_id"]) if employeeSignature.get("generalInformation_ref_id") else None,

        # SOFT DELETE FIELD
        "active": employeeSignature.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(employeeSignature["createdBy"]) if employeeSignature.get("createdBy") else None,
        "updatedBy": str(employeeSignature["updatedBy"]) if employeeSignature.get("updatedBy") else None,
        "createdAt": employeeSignature["createdAt"].isoformat() if employeeSignature.get("createdAt") else None,
        "updatedAt": employeeSignature["updatedAt"].isoformat() if employeeSignature.get("updatedAt") else None,
    }