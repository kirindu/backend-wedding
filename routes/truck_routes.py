from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from models.truck_model import TruckModel
from config.database import trucks_collection
from schemas.truck_scheme import truck_helper
from utils.response_helper import success_response, error_response
from bson import ObjectId

router = APIRouter()


@router.post("/")
async def create_truck(truck: TruckModel):
    try:
        data = truck.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await trucks_collection.insert_one(data)
        created = await trucks_collection.find_one({"_id": new.inserted_id})
        return success_response(truck_helper(created), msg="Truck creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear truck: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_trucks():
    try:
        result = [truck_helper(truck) async for truck in trucks_collection.find({"active": True}).sort("truckNumber", 1)]
        return success_response(result, msg="Lista de trucks obtenida")
    except Exception as e:
        return error_response(f"Error al obtener trucks: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_truck(id: str):
    try:
        truck = await trucks_collection.find_one({"_id": ObjectId(id)})
        if truck:
            return success_response(truck_helper(truck), msg="Truck encontrado")
        return error_response("Truck no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener truck: {str(e)}")


@router.put("/{id}")
async def update_truck(id: str, truck: TruckModel):
    try:
        update_data = truck.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await trucks_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Truck no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await trucks_collection.find_one({"_id": ObjectId(id)})
        return success_response(truck_helper(updated), msg="Truck actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar truck: {str(e)}")


@router.delete("/{id}")
async def delete_truck(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        truck = await trucks_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not truck:
            return error_response(
                "Truck no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await trucks_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Truck eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar truck: {str(e)}")