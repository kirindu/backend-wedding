def load_helper(load) -> dict:
    return {
        "id": str(load["_id"]),
        "firstStopTime": load.get("firstStopTime"),
        "route_id": str(load["route_id"]) if load.get("route_id") else None,
        "routeNumber": load.get("routeNumber", ""),
        "lastStopTime": load.get("lastStopTime"),
        "landFillTimeIn": load.get("landFillTimeIn"),
        "landFillTimeOut": load.get("landFillTimeOut"),
        "grossWeight": load.get("grossWeight"),
        "tareWeight": load.get("tareWeight"),
        "tons": load.get("tons"),
        "landFill_id": str(load["landFill_id"]) if load.get("landFill_id") else None,
        "landfillName": load.get("landfillName", ""),
        "material_id": str(load["material_id"]) if load.get("material_id") else None,
        "materialName": load.get("materialName", ""),
        "ticketNumber": load.get("ticketNumber"),
        "note": load.get("note"),
        "images": load.get("images", []),
        
        # 🆕 Nueva referencia al coversheet padre
        "coversheet_ref_id": str(load["coversheet_ref_id"]) if load.get("coversheet_ref_id") else None,
        
        # 🆕 Campo de soft delete
        "active": load.get("active", True),
        
        # AUDIT FIELDS  
        "createdAt": load["createdAt"].isoformat() if load.get("createdAt") else None,
        "updatedAt": load["updatedAt"].isoformat() if load.get("updatedAt") else None   
    }