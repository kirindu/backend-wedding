def downtime_helper(downtime) -> dict:
    return {
        "id": str(downtime["_id"]),
        "truck_id": str(downtime["truck_id"]) if downtime.get("truck_id") else None,
        "truckNumber": downtime.get("truckNumber"),
        "startTime": downtime.get("startTime"),
        "endTime": downtime.get("endTime"),
        "downtimeReason": downtime.get("downtimeReason"),
        
        # 🆕 Nueva referencia al coversheet padre
        "coversheet_ref_id": str(downtime["coversheet_ref_id"]) if downtime.get("coversheet_ref_id") else None,
        
        # 🆕 Campo de soft delete
        "active": downtime.get("active", True),
        
        # AUDIT FIELDS
        "createdAt": downtime["createdAt"].isoformat() if downtime.get("createdAt") else None,
        "updatedAt": downtime["updatedAt"].isoformat() if downtime.get("updatedAt") else None
    }