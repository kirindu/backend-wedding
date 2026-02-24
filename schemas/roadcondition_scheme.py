def road_condition_helper(roadcondition) -> dict:
    return {
        "id": str(roadcondition["_id"]),
        "roadConditionName": roadcondition.get("roadConditionName"),

        # SOFT DELETE FIELD
        "active": roadcondition.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(roadcondition["createdBy"]) if roadcondition.get("createdBy") else None,
        "updatedBy": str(roadcondition["updatedBy"]) if roadcondition.get("updatedBy") else None,
        "createdAt": roadcondition["createdAt"].isoformat() if roadcondition.get("createdAt") else None,
        "updatedAt": roadcondition["updatedAt"].isoformat() if roadcondition.get("updatedAt") else None,
    }