
def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        "id": str(sparetruckinfo["_id"]),
        "spareTruckNumber": sparetruckinfo["spareTruckNumber"],
        "route_id": sparetruckinfo["route_id"],
        "routeNumber": sparetruckinfo.get("routeNumber", ""),
        "leaveYard": sparetruckinfo["leaveYard"],
        "backInYard": sparetruckinfo["backInYard"],
        "startMiles": sparetruckinfo["startMiles"],
        "endMiles": sparetruckinfo["endMiles"],
        "fuel": sparetruckinfo["fuel"],
        
                      # AUDIT FIELDS

        "createdAt": sparetruckinfo["createdAt"].isoformat() if sparetruckinfo.get("createdAt") else None,
        "updatedAt": sparetruckinfo["updatedAt"].isoformat() if sparetruckinfo.get("updatedAt") else None
    }