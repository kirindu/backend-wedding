def incident_detail_helper(incidentdetail) -> dict:
    return {

        # INCIDENT DETAILS
        "id": str(incidentdetail["_id"]),

        # ✅ Corregido: todos los campos usan .get() para evitar KeyError si son None
        "incidentDescription": incidentdetail.get("incidentDescription"),
        "actionEventCondition": incidentdetail.get("actionEventCondition"),
        "wereAnyVehiclesTowed": incidentdetail.get("wereAnyVehiclesTowed"),
        "wasAnyOneHurt": incidentdetail.get("wasAnyOneHurt"),
        "describeAnyInjuries": incidentdetail.get("describeAnyInjuries"),
        "damageToAceTruck": incidentdetail.get("damageToAceTruck"),
        "whatDamageWasDone": incidentdetail.get("whatDamageWasDone"),
        "incidentInThePastYear": incidentdetail.get("incidentInThePastYear"),
        "listDatesOfIncidents": incidentdetail.get("listDatesOfIncidents"),

        "images": incidentdetail.get("images", []),
        "image_path": incidentdetail.get("image_path"),

        # Referencia al padre
        "generalInformation_ref_id": str(incidentdetail["generalInformation_ref_id"]) if incidentdetail.get("generalInformation_ref_id") else None,

        # SOFT DELETE FIELD
        "active": incidentdetail.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(incidentdetail["createdBy"]) if incidentdetail.get("createdBy") else None,
        "updatedBy": str(incidentdetail["updatedBy"]) if incidentdetail.get("updatedBy") else None,
        "createdAt": incidentdetail["createdAt"].isoformat() if incidentdetail.get("createdAt") else None,
        "updatedAt": incidentdetail["updatedAt"].isoformat() if incidentdetail.get("updatedAt") else None,
    }