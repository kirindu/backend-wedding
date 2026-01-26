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

        # SINGLE RELATIONSHIPS
        "truck_id": str(coversheet["truck_id"]) if coversheet.get("truck_id") else None,
        "route_id": str(coversheet["route_id"]) if coversheet.get("route_id") else None,
        "driver_id": str(coversheet["driver_id"]) if coversheet.get("driver_id") else None,
        
        # Additional fields (denormalized data)
        "truckNumber": coversheet.get("truckNumber", ""),
        "routeNumber": coversheet.get("routeNumber", ""),
        "driverName": coversheet.get("driverName", ""),
        
        # FIELDS
        "date": coversheet["date"].isoformat() if coversheet.get("date") else None,
        "notes": coversheet.get("notes"),
        
        # SOFT DELETE FIELD
        "active": coversheet.get("active", True),  # ✅ Campo de borrado lógico
        
        # AUDIT FIELDS
        "createdAt": coversheet["createdAt"].isoformat() if coversheet.get("createdAt") else None,
        "updatedAt": coversheet["updatedAt"].isoformat() if coversheet.get("updatedAt") else None
        
    }