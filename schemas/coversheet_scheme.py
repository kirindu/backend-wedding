def coversheet_helper(coversheet) -> dict:
    return {
        # TRUCK INFO
        "id": str(coversheet["_id"]),
        "clockIn": coversheet["clockIn"],
        "leaveYard": coversheet["leaveYard"],
        "backInYard": coversheet["backInYard"],
        "clockOut": coversheet["clockOut"],
        "startMiles": coversheet["startMiles"],
        "endMiles": coversheet["endMiles"],
        "fuel": coversheet["fuel"],
        # "clockInTrainee": coversheet["clockInTrainee"],
        # "clockOutTrainee": coversheet["clockOutTrainee"],   
        
        # RELATIONSHIPS (arrays removed, children reference parent)
        # No more: "spareTruckInfo_id", "downtime_id", "load_id"
        
        # SINGLE RELATIONSHIPS
        "truck_id": str(coversheet["truck_id"]),
        "route_id": str(coversheet["route_id"]),
        "driver_id": str(coversheet["driver_id"]),
        
        # Additional fields (denormalized data)
        "truckNumber": coversheet.get("truckNumber", ""),
        "routeNumber": coversheet.get("routeNumber", ""),
        "driverName": coversheet.get("driverName", ""),
        
        # FIELDS
        "date": coversheet["date"].isoformat() if coversheet.get("date") else None,
        "notes": coversheet.get("notes"),
        "active": coversheet.get("active", True),
        
        # AUDIT FIELDS
        "createdAt": coversheet["createdAt"].isoformat() if coversheet.get("createdAt") else None,
        "updatedAt": coversheet["updatedAt"].isoformat() if coversheet.get("updatedAt") else None
        
    }