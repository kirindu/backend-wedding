def safety_person_notified_helper(safetyPersonNotified) -> dict:
    return {
        "id": str(safetyPersonNotified["_id"]),

        # ✅ Corregido: era safetyPersonNotified["routeNumber"] y safetyPersonNotified["lob"], campos que no existen en el modelo
        "safetyPersonNotifiedName": safetyPersonNotified.get("safetyPersonNotifiedName"),

        # SOFT DELETE FIELD
        "active": safetyPersonNotified.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(safetyPersonNotified["createdBy"]) if safetyPersonNotified.get("createdBy") else None,
        "updatedBy": str(safetyPersonNotified["updatedBy"]) if safetyPersonNotified.get("updatedBy") else None,
        "createdAt": safetyPersonNotified["createdAt"].isoformat() if safetyPersonNotified.get("createdAt") else None,
        "updatedAt": safetyPersonNotified["updatedAt"].isoformat() if safetyPersonNotified.get("updatedAt") else None,
    }