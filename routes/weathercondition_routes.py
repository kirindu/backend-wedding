from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.weathercondition_model import WeatherConditionModel

# Configuración de la base de datos y colecciones
from config.database import weatherConditions_collection

# Esquemas
from schemas.weathercondition_scheme import weather_condition_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_weather_condition(weather_condition: WeatherConditionModel):
    try:
        data = weather_condition.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await weatherConditions_collection.insert_one(data)
        created = await weatherConditions_collection.find_one({"_id": new.inserted_id})
        return success_response(weather_condition_helper(created), msg="Weather condition creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear weather condition: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_weather_conditions():
    try:
        weather_conditions = [
            weather_condition_helper(w)
            async for w in weatherConditions_collection.find({"active": True}).sort("weatherName", 1)
        ]
        return success_response(weather_conditions, msg="Lista de weather conditions obtenida")
    except Exception as e:
        return error_response(f"Error al obtener weather conditions: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_weather_condition(id: str):
    try:
        weather_condition = await weatherConditions_collection.find_one({"_id": ObjectId(id)})
        if weather_condition:
            return success_response(weather_condition_helper(weather_condition), msg="Weather condition encontrada")
        return error_response("Weather condition no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener weather condition: {str(e)}")


@router.put("/{id}")
async def update_weather_condition(id: str, weather_condition: WeatherConditionModel):
    try:
        update_data = weather_condition.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await weatherConditions_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Weather condition no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        updated = await weatherConditions_collection.find_one({"_id": ObjectId(id)})
        return success_response(weather_condition_helper(updated), msg="Weather condition actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar weather condition: {str(e)}")


@router.delete("/{id}")
async def delete_weather_condition(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        weather_condition = await weatherConditions_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not weather_condition:
            return error_response(
                "Weather condition no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await weatherConditions_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Weather condition eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar weather condition: {str(e)}")