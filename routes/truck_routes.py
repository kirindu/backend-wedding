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
        new = await trucks_collection.insert_one(truck.model_dump())
        created = await trucks_collection.find_one({"_id": new.inserted_id})
        return success_response(truck_helper(created), msg="Truck creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear truck: {str(e)}")

@router.get("/")
async def get_all_trucks():
    try:
        result = [truck_helper(truck) async for truck in trucks_collection.find()]
        return success_response(result, msg="Lista de trucks obtenida")
    except Exception as e:
        return error_response(f"Error al obtener trucks: {str(e)}")

@router.get("/{id}")
async def get_truck(id: str):
    try:
        truck = await trucks_collection.find_one({"_id": ObjectId(id)})
        if truck:
            return success_response(truck_helper(truck), msg="Truck encontrado")
        return error_response("Truck no encontrado", status_code=404)
    except Exception as e:
        return error_response(f"Error al obtener truck: {str(e)}")

@router.put("/{id}")
async def update_truck(id: str, truck: TruckModel):
    try:
        res = await trucks_collection.update_one({"_id": ObjectId(id)}, {"$set": truck.model_dump()})
        if res.matched_count == 0:
            return error_response("Truck no encontrado", status_code=404)
        updated = await trucks_collection.find_one({"_id": ObjectId(id)})
        return success_response(truck_helper(updated), msg="Truck actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar truck: {str(e)}")

@router.delete("/{id}")
async def delete_truck(id: str):
    try:
        res = await trucks_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Truck eliminado")
        return error_response("Truck no encontrado", status_code=404)
    except Exception as e:
        return error_response(f"Error al eliminar truck: {str(e)}")
