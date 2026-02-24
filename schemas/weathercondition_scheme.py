def weather_condition_helper(weathercondition) -> dict:
    return {
        "id": str(weathercondition["_id"]),

        # ✅ Corregido: usando .get() para evitar KeyError
        "weatherName": weathercondition.get("weatherName"),

        # SOFT DELETE FIELD
        "active": weathercondition.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(weathercondition["createdBy"]) if weathercondition.get("createdBy") else None,
        "updatedBy": str(weathercondition["updatedBy"]) if weathercondition.get("updatedBy") else None,
        "createdAt": weathercondition["createdAt"].isoformat() if weathercondition.get("createdAt") else None,
        "updatedAt": weathercondition["updatedAt"].isoformat() if weathercondition.get("updatedAt") else None,
    }