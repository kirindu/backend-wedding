def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        "id": str(sparetruckinfo["_id"]),
        "spareTruckNumber": sparetruckinfo.get("spareTruckNumber"),
        "route_id": str(sparetruckinfo["route_id"]) if sparetruckinfo.get("route_id") else None,
        "routeNumber": sparetruckinfo.get("routeNumber", ""),
        "leaveYard": sparetruckinfo.get("leaveYard"),
        "backInYard": sparetruckinfo.get("backInYard"),
        "startMiles": sparetruckinfo.get("startMiles"),
        "endMiles": sparetruckinfo.get("endMiles"),
        "fuel": sparetruckinfo.get("fuel"),
        
        # 🆕 Nueva referencia al coversheet padre
        "coversheet_ref_id": str(sparetruckinfo["coversheet_ref_id"]) if sparetruckinfo.get("coversheet_ref_id") else None,
        
        # 🆕 Campo de soft delete
        "active": sparetruckinfo.get("active", True),
        
        # AUDIT FIELDS
        "createdAt": sparetruckinfo["createdAt"].isoformat() if sparetruckinfo.get("createdAt") else None,
        "updatedAt": sparetruckinfo["updatedAt"].isoformat() if sparetruckinfo.get("updatedAt") else None
    }