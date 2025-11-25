
def downtime_helper(downtime) -> dict:
    return {
        "id": str(downtime["_id"]),
        "truck_id": downtime["truck_id"],
        "truckNumber": downtime["truckNumber"],
        "startTime": downtime["startTime"],
        "endTime": downtime["endTime"],
        "downtimeReason": downtime["downtimeReason"],
        
              # AUDIT FIELDS
        
        "createdAt": downtime["createdAt"].isoformat() if downtime.get("createdAt") else None,
        "updatedAt": downtime["updatedAt"].isoformat() if downtime.get("updatedAt") else None
        
        
    }