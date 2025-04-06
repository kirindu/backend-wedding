
def coversheet_helper(coversheet) -> dict:
    return {
        "id": str(coversheet["_id"]),
        "truckInfo_clockIn": coversheet["truckInfo_clockIn"],
        "truckInfo_leaveYard": coversheet["truckInfo_leaveYard"],
        "truckInfo_backInYard": coversheet["truckInfo_backInYard"],
        "truckInfo_clockOut": coversheet["truckInfo_clockOut"],
        "truckInfo_startMiles": coversheet["truckInfo_startMiles"],
        "truckInfo_endMiles": coversheet["truckInfo_endMiles"],
        "truckInfo_fuel": coversheet["truckInfo_fuel"],
        
        "spareTruckInfo_spareTruckNumber": coversheet["spareTruckInfo_spareTruckNumber"],
        "spareTruckInfo_routeNumber": coversheet["spareTruckInfo_routeNumber"],
        "spareTruckInfo_leaveYard": coversheet["spareTruckInfo_leaveYard"],
        "spareTruckInfo_backInYard": coversheet["spareTruckInfo_backInYard"],
        "spareTruckInfo_startMiles": coversheet["spareTruckInfo_startMiles"],
        "spareTruckInfo_endMiles": coversheet["spareTruckInfo_endMiles"],
        "spareTruckInfo_fuel": coversheet["spareTruckInfo_fuel"],
        
        "downtime_truckNumber": coversheet["downtime_truckNumber"],
        "downtime_startTime": coversheet["downtime_startTime"],
        "downtime_downtimeReason": coversheet["downtime_downtimeReason"],
        
        "truck_id": coversheet["truck_id"],
        "route_id": coversheet["route_id"],
        "driver_id": coversheet["driver_id"],
        
        "creationDate": coversheet["creationDate"]
        
    }