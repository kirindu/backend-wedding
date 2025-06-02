
def landfill_helper(landfill) -> dict:
    return {
        "id": str(landfill["_id"]),
        "name": landfill["name"],
        "createdAt": landfill["createdAt"].isoformat() if "createdAt" in landfill else None,
    }