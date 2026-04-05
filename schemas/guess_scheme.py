def guess_helper(guess) -> dict:
    return {
        "id": str(guess["_id"]),
        "nombre": guess.get("nombre"),
        "cantidadAdultos": guess.get("cantidadAdultos"),
        "cantidadNinos": guess.get("cantidadNinos"),
        "comentarios": guess.get("comentarios"),

  
        # SOFT DELETE FIELD
        "active": guess.get("active", True),

        # AUDIT FIELDS
        "createdAt": guess["createdAt"].isoformat() if guess.get("createdAt") else None,
        "updatedAt": guess["updatedAt"].isoformat() if guess.get("updatedAt") else None,
    }