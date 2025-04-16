
def truck_helper(truck) -> dict:
    return {
        "id": str(truck["_id"]),
        "truckNumber": truck["truckNumber"],
        "createdAt": truck["createdAt"]
    }