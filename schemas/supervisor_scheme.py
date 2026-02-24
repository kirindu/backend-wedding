def supervisor_helper(supervisor) -> dict:
    return {
        "id": str(supervisor["_id"]),

        # ✅ Corregido: era supervisor["routeNumber"] y supervisor["lob"], campos que no existen en el modelo
        "supervisorName": supervisor.get("supervisorName"),

        # SOFT DELETE FIELD
        "active": supervisor.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(supervisor["createdBy"]) if supervisor.get("createdBy") else None,
        "updatedBy": str(supervisor["updatedBy"]) if supervisor.get("updatedBy") else None,
        "createdAt": supervisor["createdAt"].isoformat() if supervisor.get("createdAt") else None,
        "updatedAt": supervisor["updatedAt"].isoformat() if supervisor.get("updatedAt") else None,
    }