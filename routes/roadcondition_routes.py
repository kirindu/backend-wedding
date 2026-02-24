from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.roadcondition_model import RoadConditionModel

# Configuración de la base de datos y colecciones
from config.database import roadConditions_collection

# Esquemas
from schemas.roadcondition_scheme import road_condition_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_road_condition(road_condition: RoadConditionModel):
    try:
        data = road_condition.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await roadConditions_collection.insert_one(data)
        created = await roadConditions_collection.find_one({"_id": new.inserted_id})
        return success_response(road_condition_helper(created), msg="Road condition creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear road condition: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_road_conditions():
    try:
        road_conditions = [
            road_condition_helper(r)
            async for r in roadConditions_collection.find({"active": True}).sort("roadConditionName", 1)
        ]
        return success_response(road_conditions, msg="Lista de road conditions obtenida")
    except Exception as e:
        return error_response(f"Error al obtener road conditions: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_road_condition(id: str):
    try:
        road_condition = await roadConditions_collection.find_one({"_id": ObjectId(id)})
        if road_condition:
            return success_response(road_condition_helper(road_condition), msg="Road condition encontrada")
        return error_response("Road condition no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener road condition: {str(e)}")


@router.put("/{id}")
async def update_road_condition(id: str, road_condition: RoadConditionModel):
    try:
        update_data = road_condition.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await roadConditions_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Road condition no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        updated = await roadConditions_collection.find_one({"_id": ObjectId(id)})
        return success_response(road_condition_helper(updated), msg="Road condition actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar road condition: {str(e)}")


@router.delete("/{id}")
async def delete_road_condition(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        road_condition = await roadConditions_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not road_condition:
            return error_response(
                "Road condition no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await roadConditions_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Road condition eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar road condition: {str(e)}")