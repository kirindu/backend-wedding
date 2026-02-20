def generalinformation_helper(generalinformation) -> dict:
    return {
        
        
        
        
        
        # GENERAL INFORMATION
        "id": str(generalinformation["_id"]),
        "date": generalinformation["date"].isoformat() if generalinformation.get("date") else None,
        "trainerName": generalinformation["trainerName"],
        "employee_id": str(generalinformation["employee_id"]) if generalinformation.get("employee_id") else None,
        "truck_id": str(generalinformation["truck_id"]) if generalinformation.get("truck_id") else None,
        "dept_id": str(generalinformation["dept_id"]) if generalinformation.get("dept_id") else None,
        "supervisor_id": str(generalinformation["supervisor_id"]) if generalinformation.get("supervisor_id") else None,
        "typeOfIncident_id": str(generalinformation["typeOfIncident_id"]) if generalinformation.get("typeOfIncident_id") else None,
        "location": generalinformation["location"],
        "time": generalinformation["time"],
        "timeWorkedYears": generalinformation["timeWorkedYears"],
        "timeWorkedMonths": generalinformation["timeWorkedMonths"],
        "timeDayStarted": generalinformation["timeDayStarted"].isoformat() if generalinformation.get("timeDayStarted") else None,
        
        
        "employeeName": generalinformation.get("employeeName", ""),
        "truckNumber": generalinformation.get("truckNumber", ""),
        "deptName": generalinformation.get("deptName", ""),
        "supervisorName": generalinformation.get("supervisorName", ""),
        "typeOfIncidentName": generalinformation.get("typeOfIncidentName", ""), 

        # SOFT DELETE FIELD
        "active": generalinformation.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        "createdAt": generalinformation["createdAt"].isoformat() if generalinformation.get("createdAt") else None,
        "updatedAt": generalinformation["updatedAt"].isoformat() if generalinformation.get("updatedAt") else None
        
    }