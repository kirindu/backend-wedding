def truck_helper(truck) -> dict:
    return {
        "id": str(truck["_id"]),

        # ✅ Corregido: usando .get() para evitar KeyError
        "truckNumber": truck.get("truckNumber"),

        # SOFT DELETE FIELD
        "active": truck.get("active", True),

        # AUDIT FIELDS
        "createdBy": str(truck["createdBy"]) if truck.get("createdBy") else None,
        "updatedBy": str(truck["updatedBy"]) if truck.get("updatedBy") else None,
        "createdAt": truck["createdAt"].isoformat() if truck.get("createdAt") else None,
        "updatedAt": truck["updatedAt"].isoformat() if truck.get("updatedAt") else None,
    }