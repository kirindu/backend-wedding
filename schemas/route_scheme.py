def route_helper(route) -> dict:
    return {
        "id": str(route["_id"]),
        "routeNumber": route["routeNumber"],
        "createdAt": route["createdAt"]
    }
