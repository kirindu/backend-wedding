from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.safetypersonnotified_model import SafetyPersonNotifiedModel

# Configuración de la base de datos y colecciones
from config.database import safetyPersonsNotified_collection

# Esquemas
from schemas.safetypersonnotified_scheme import safety_person_notified_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_safety_person_notified(safety_person_notified: SafetyPersonNotifiedModel):
    try:
        data = safety_person_notified.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await safetyPersonsNotified_collection.insert_one(data)
        created = await safetyPersonsNotified_collection.find_one({"_id": new.inserted_id})
        return success_response(safety_person_notified_helper(created), msg="Safety person notified creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear safety person notified: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_safety_persons_notified():
    try:
        result = [
            safety_person_notified_helper(s)
            async for s in safetyPersonsNotified_collection.find({"active": True}).sort("safetyPersonNotifiedName", 1)
        ]
        return success_response(result, msg="Lista de safety persons notified obtenida")
    except Exception as e:
        return error_response(f"Error al obtener safety persons notified: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_safety_person_notified(id: str):
    try:
        safety_person_notified = await safetyPersonsNotified_collection.find_one({"_id": ObjectId(id)})
        if safety_person_notified:
            return success_response(safety_person_notified_helper(safety_person_notified), msg="Safety person notified encontrado")
        return error_response("Safety person notified no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener safety person notified: {str(e)}")


@router.put("/{id}")
async def update_safety_person_notified(id: str, safety_person_notified: SafetyPersonNotifiedModel):
    try:
        update_data = safety_person_notified.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await safetyPersonsNotified_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Safety person notified no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await safetyPersonsNotified_collection.find_one({"_id": ObjectId(id)})
        return success_response(safety_person_notified_helper(updated), msg="Safety person notified actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar safety person notified: {str(e)}")


@router.delete("/{id}")
async def delete_safety_person_notified(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        safety_person_notified = await safetyPersonsNotified_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not safety_person_notified:
            return error_response(
                "Safety person notified no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await safetyPersonsNotified_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Safety person notified eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar safety person notified: {str(e)}")