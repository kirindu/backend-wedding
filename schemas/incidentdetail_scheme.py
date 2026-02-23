def incident_detail_helper(incidentdetail) -> dict:
    return {
        
        # INCIDENT DETAILS
        
        "id": str(incidentdetail["_id"]),
        "incidentDescription": incidentdetail["incidentDescription"],
        "actionEventCondition": incidentdetail["actionEventCondition"],
        "wereAnyVehiclesTowed": incidentdetail["wereAnyVehiclesTowed"],
        "wasAnyOneHurt": incidentdetail["wasAnyOneHurt"],
        "describeAnyInjuries": incidentdetail["describeAnyInjuries"],
        "damageToAceTruck": incidentdetail["damageToAceTruck"],
        "whatDamageWasDone": incidentdetail["whatDamageWasDone"],
        "incidentInThePastYear": incidentdetail["incidentInThePastYear"],
        "listDatesOfIncidents": incidentdetail["listDatesOfIncidents"],
        
        "images": incidentdetail.get("images", []),
        "image_path": incidentdetail.get("image_path", None),
        
        # 🆕 referencia al padre
        "generalInformation_ref_id": str(incidentdetail["generalInformation_ref_id"]) if incidentdetail.get("generalInformation_ref_id") else None,     
        

        # SOFT DELETE FIELD
        "active": incidentdetail.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        
        "createdBy" : str(incidentdetail["createdBy"]) if incidentdetail.get("createdBy") else None,
        "updatedBy" : str(incidentdetail["updatedBy"]) if incidentdetail.get("updatedBy") else None,
        "createdAt": incidentdetail["createdAt"].isoformat() if incidentdetail.get("createdAt") else None,
        "updatedAt": incidentdetail["updatedAt"].isoformat() if incidentdetail.get("updatedAt") else None,
        
    }