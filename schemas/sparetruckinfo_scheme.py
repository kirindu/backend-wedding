
def sparetruckinfo_helper(sparetruckinfo) -> dict:
    return {
        "id": str(sparetruckinfo["_id"]),
        "spareTruckNumber": sparetruckinfo["spareTruckNumber"],
        "routeNumber": sparetruckinfo["routeNumber"],
        "leaveYard": sparetruckinfo["leaveYard"],
        "backInYard": sparetruckinfo["backInYard"],
        "startMiles": sparetruckinfo["startMiles"],
        "endMiles": sparetruckinfo["endMiles"],
        "fuel": sparetruckinfo["fuel"]
    }