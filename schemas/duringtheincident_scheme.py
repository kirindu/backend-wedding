def during_the_incident_helper(duringIncident) -> dict:
    return {
        "id": str(duringIncident["_id"]),
        "usingElectronicDevice": duringIncident.get("usingElectronicDevice"),
        "taskPerfomed": duringIncident.get("taskPerfomed"),
        "whereWereYouComingFrom": duringIncident.get("whereWereYouComingFrom"),
        "whereWereYouGoingTo": duringIncident.get("whereWereYouGoingTo"),
        "howFastWereYouGoing": duringIncident.get("howFastWereYouGoing"),
        "directionYouWereTraveling_id": duringIncident.get("directionYouWereTraveling_id"),
        "weatherConditions_id": duringIncident.get("weatherConditions_id"),
        "roadConditions_id": duringIncident.get("roadConditions_id"),
        "wasThisIncidentInAnIntersection": duringIncident.get("wasThisIncidentInAnIntersection"),
        "witness": duringIncident.get("witness"),
        "witnessPhone": duringIncident.get("witnessPhone"),
        
        # 🆕 referencia al padre
        "generalInformation_ref_id": str(duringIncident["generalInformation_ref_id"]) if duringIncident.get("generalInformation_ref_id") else None,     
        
    
       # SOFT DELETE FIELD
        "active": duringIncident.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(duringIncident["createdBy"]) if duringIncident.get("createdBy") else None,
        "updatedBy" : str(duringIncident["updatedBy"]) if duringIncident.get("updatedBy") else None,
        "createdAt": duringIncident["createdAt"].isoformat() if duringIncident.get("createdAt") else None,
        "updatedAt": duringIncident["updatedAt"].isoformat() if duringIncident.get("updatedAt") else None,
    }