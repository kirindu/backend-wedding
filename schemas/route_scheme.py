def route_helper(route) -> dict:
    return {
        "id": str(route["_id"]),
        "routeNumber": route["routeNumber"],
        "lob": route["lob"],
        "active": route["active"],
        "createdAt": route["createdAt"]
    }