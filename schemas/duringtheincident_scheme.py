def during_the_incident_helper(duringIncident) -> dict:
    return {
        "id": str(duringIncident["_id"]),
        "usingElectronicDevice": duringIncident.get("usingElectronicDevice"),
        "taskPerfomed": duringIncident.get("taskPerfomed"),
        "whereWereYouComingFrom": duringIncident.get("whereWereYouComingFrom"),
        "whereWereYouGoingTo": duringIncident.get("whereWereYouGoingTo"),
        "howFastWereYouGoing": duringIncident.get("howFastWereYouGoing"),

        # IDs de referencia (como string para el frontend)
        "directionYouWereTraveling_id": str(duringIncident["directionYouWereTraveling_id"]) if duringIncident.get("directionYouWereTraveling_id") else None,
        "weatherConditions_id": str(duringIncident["weatherConditions_id"]) if duringIncident.get("weatherConditions_id") else None,
        "roadConditions_id": str(duringIncident["roadConditions_id"]) if duringIncident.get("roadConditions_id") else None,

        # ✅ Nombres denormalizados - leídos del campo guardado, no del ObjectId
        "directionName": duringIncident.get("directionName"),
        "weatherName": duringIncident.get("weatherName"),
        "roadConditionName": duringIncident.get("roadConditionName"),

        "wasThisIncidentInAnIntersection": duringIncident.get("wasThisIncidentInAnIntersection"),
        "witness": duringIncident.get("witness"),
        "witnessPhone": duringIncident.get("witnessPhone"),

        # Referencia al padre
        "generalInformation_ref_id": str(duringIncident["generalInformation_ref_id"]) if duringIncident.get("generalInformation_ref_id") else None,

        # SOFT DELETE FIELD
        "active": duringIncident.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(duringIncident["createdBy"]) if duringIncident.get("createdBy") else None,
        "updatedBy": str(duringIncident["updatedBy"]) if duringIncident.get("updatedBy") else None,
        "createdAt": duringIncident["createdAt"].isoformat() if duringIncident.get("createdAt") else None,
        "updatedAt": duringIncident["updatedAt"].isoformat() if duringIncident.get("updatedAt") else None,
    }