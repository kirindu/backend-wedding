
def landfill_helper(landfill) -> dict:
    return {
        "id": str(landfill["_id"]),
        "landfillName": landfill["landfillName"],
        "createdAt": landfill["createdAt"].isoformat() if "createdAt" in landfill else None,
    }