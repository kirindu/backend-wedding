def incidentdetail_helper(incidentdetail) -> dict:
    return {
        
        
        
        
        
        # GENERAL INFORMATION
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
        
        

        # SOFT DELETE FIELD
        "active": incidentdetail.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        "createdAt": incidentdetail["createdAt"].isoformat() if incidentdetail.get("createdAt") else None,
        "updatedAt": incidentdetail["updatedAt"].isoformat() if incidentdetail.get("updatedAt") else None
        
    }