def during_the_incident_helper(duringIncident) -> dict:
    return {
        "id": str(duringIncident["_id"]),

        "usingElectronicDevice": duringIncident.get("usingElectronicDevice"),
        "taskPerfomed": duringIncident.get("taskPerfomed"),

        "wasSafetyDeptNotified": duringIncident.get("wasSafetyDeptNotified"),
        "didYouTakePictures": duringIncident.get("didYouTakePictures"),
        "howFastWereYouGoing": duringIncident.get("howFastWereYouGoing"),

        # ✅ IDs de referencia — nombres alineados con el frontend y el modelo
        "safetyPersonNotified_id": str(duringIncident["safetyPersonNotified_id"]) if duringIncident.get("safetyPersonNotified_id") else None,
        "whoDidYouSendThePicturesTo_id": str(duringIncident["whoDidYouSendThePicturesTo_id"]) if duringIncident.get("whoDidYouSendThePicturesTo_id") else None,
        "directionYouWereTraveling_id": str(duringIncident["directionYouWereTraveling_id"]) if duringIncident.get("directionYouWereTraveling_id") else None,
        "weatherCondition_id": str(duringIncident["weatherCondition_id"]) if duringIncident.get("weatherCondition_id") else None,
        "roadCondition_id": str(duringIncident["roadCondition_id"]) if duringIncident.get("roadCondition_id") else None,

        # ✅ Nombres denormalizados
        "safetyPersonNotifiedName": duringIncident.get("safetyPersonNotifiedName"),
        "whoDidYouSendThePictureToName": duringIncident.get("whoDidYouSendThePictureToName"),
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