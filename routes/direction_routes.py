
# Librerias
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.direction_model import DirectionModel

# Configuración de la base de datos y colecciones
from config.database import directions_collection

# Esquemas
from schemas.direction_scheme import direction_helper

# Rutas
router = APIRouter()

# CRUD para Direction
@router.post("/")
async def create_direction(direction: DirectionModel):
    try:
        data = direction.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await directions_collection.insert_one(data)
        created = await directions_collection.find_one({"_id": new.inserted_id})
        return success_response(direction_helper(created), msg="Direction creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el direction: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_directions():
    try:
        directions = [direction_helper(direction) async for direction in directions_collection.find().sort("directionName", 1)]
        return success_response(directions, msg="Lista de directions obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los directions: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_direction(id: str):
    direction = await directions_collection.find_one({"_id": ObjectId(id)})
    if direction:
        return success_response(direction_helper(direction), msg="Direction encontrado")
    return error_response("Direction no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_direction(id: str, direction: DirectionModel):
    update_data = direction.model_dump()
    update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

    res = await directions_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if res.matched_count == 0:
        return error_response("Direction no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await directions_collection.find_one({"_id": ObjectId(id)})
    return success_response(direction_helper(updated), msg="Direction actualizado")

@router.delete("/{id}")
async def delete_direction(id: str):
    """
    Soft delete a direction by setting active=False
    ❌ Ya NO es un hard delete
    """
    try:
        # Verificar que el direction existe y está activo
        direction = await directions_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not direction:
            return error_response(
                "Direction no encontrado o ya fue eliminado", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 🆕 Soft delete: marcar como inactivo
        await directions_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="Direction eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar direction: {str(e)}")

# @router.delete("/{id}")
# async def delete_direction(id: str):
#     res = await directions_collection.delete_one({"_id": ObjectId(id)})
#     if res.deleted_count:
#         return success_response(None, msg="Direction eliminado")
#     return error_response("Direction no encontrado", status_code=status.HTTP_404_NOT_FOUND)    