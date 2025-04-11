
def truck_helper(truck) -> dict:
    return {
        "id": str(truck["_id"]),
        "truckNumber": truck["nombreTruck"],
        "createdAt": truck["createdAt"]
    }