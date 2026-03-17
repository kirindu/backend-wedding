def general_information_helper(generalinformation) -> dict:
    return {

        # GENERAL INFORMATION
        "id": str(generalinformation["_id"]),
        "date": generalinformation["date"].isoformat() if generalinformation.get("date") else None,
        "trainerName": generalinformation.get("trainerName"),

        # IDs de referencia (como string para el frontend)
        "employee_id": str(generalinformation["employee_id"]) if generalinformation.get("employee_id") else None,
        "truck_id": str(generalinformation["truck_id"]) if generalinformation.get("truck_id") else None,
        "dept_id": str(generalinformation["dept_id"]) if generalinformation.get("dept_id") else None,
        "supervisor_id": str(generalinformation["supervisor_id"]) if generalinformation.get("supervisor_id") else None,
        "typeOfIncident_id": str(generalinformation["typeOfIncident_id"]) if generalinformation.get("typeOfIncident_id") else None,

        # ✅ Nombres denormalizados - leídos del campo guardado, no del ObjectId
        "employeeName": generalinformation.get("employeeName"),
        "truckNumber": generalinformation.get("truckNumber"),       
        "deptName": generalinformation.get("deptName"),
        "supervisorName": generalinformation.get("supervisorName"), 
        "typeOfIncidentName": generalinformation.get("typeOfIncidentName"),
        "location": generalinformation.get("location"),
        "time": generalinformation.get("time"),
        "timeWorkedYears": generalinformation.get("timeWorkedYears"),
        "timeWorkedMonths": generalinformation.get("timeWorkedMonths"),
        "timeDayStarted": generalinformation.get("timeDayStarted"),

        # SOFT DELETE FIELD
        "active": generalinformation.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(generalinformation["createdBy"]) if generalinformation.get("createdBy") else None,
        "updatedBy": str(generalinformation["updatedBy"]) if generalinformation.get("updatedBy") else None,
        "createdAt": generalinformation["createdAt"].isoformat() if generalinformation.get("createdAt") else None,
        "updatedAt": generalinformation["updatedAt"].isoformat() if generalinformation.get("updatedAt") else None,
    }