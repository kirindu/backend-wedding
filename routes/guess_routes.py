# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelos
from models.guess_model import GuessModel

# Configuración de la base de datos y colecciones
from config.database import guess_collection

# Esquemas
from schemas.guess_scheme import guess_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_guess(guess: GuessModel):
    try:
        data = guess.model_dump()

        # Audit fields
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        new = await guess_collection.insert_one(data)
        created = await guess_collection.find_one({"_id": new.inserted_id})

        return success_response(
            guess_helper(created),
            msg="Guess creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear guess: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_guesses():
    try:
        guesses = [
            guess_helper(g)
            async for g in guess_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(guesses, msg="Lista de guesses obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener guesses: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_guess(id: str):
    try:
        guess = await guess_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if guess:
            return success_response(
                guess_helper(guess),
                msg="Guess encontrada"
            )
        return error_response(
            "Guess no encontrada",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener guess: {str(e)}")


@router.put("/{id}")
async def update_guess(id: str, guess: GuessModel):
    try:
        data = guess.model_dump(exclude_unset=True)
        data.pop("active", None)

        # ✅ Agrega esto
        if not data:
            return error_response("No se enviaron campos para actualizar")

        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await guess_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "Guess no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await guess_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            guess_helper(updated),
            msg="Guess actualizada"
        )
    except Exception as e:
        return error_response(f"Error al actualizar guess: {str(e)}")


@router.delete("/{id}")
async def delete_guess(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        guess = await guess_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not guess:
            return error_response(
                "Guess no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await guess_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="Guess eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar guess: {str(e)}")

