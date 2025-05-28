
def downtime_helper(downtime) -> dict:
    return {
        "id": str(downtime["_id"]),
        "truck_id": downtime["truck_id"],
        "truckNumber": downtime["truckNumber"],
        "startTime": downtime["startTime"],
        "endTime": downtime["endTime"],
        "downtimeReason": downtime["downtimeReason"]
    }