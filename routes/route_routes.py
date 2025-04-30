from fastapi import APIRouter, status
from models.route_model import RouteModel
from config.database import routes_collection
from schemas.route_scheme import route_helper
from bson import ObjectId
from utils.response_helper import success_response, error_response

router = APIRouter()

@router.post("/")
async def create_route(route: RouteModel):
    try:
        new = await routes_collection.insert_one(route.model_dump())
        created = await routes_collection.find_one({"_id": new.inserted_id})
        return success_response(route_helper(created), msg="Ruta creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear ruta: {str(e)}")

@router.get("/")
async def get_all_routes():
    try:
        routes = [route_helper(route) async for route in routes_collection.find()]
        return success_response(routes, msg="Listado de rutas obtenido")
    except Exception as e:
        return error_response(f"Error al obtener rutas: {str(e)}")

@router.get("/{id}")
async def get_route(id: str):
    try:
        route = await routes_collection.find_one({"_id": ObjectId(id)})
        if route:
            return success_response(route_helper(route), msg="Ruta encontrada")
        return error_response("Ruta no encontrada", status_code=404)
    except Exception as e:
        return error_response(f"Error al obtener ruta: {str(e)}")

@router.put("/{id}")
async def update_route(id: str, route: RouteModel):
    try:
        res = await routes_collection.update_one({"_id": ObjectId(id)}, {"$set": route.model_dump()})
        if res.matched_count == 0:
            return error_response("Ruta no encontrada", status_code=404)
        updated = await routes_collection.find_one({"_id": ObjectId(id)})
        return success_response(route_helper(updated), msg="Ruta actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar ruta: {str(e)}")

@router.delete("/{id}")
async def delete_route(id: str):
    try:
        res = await routes_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Ruta eliminada")
        return error_response("Ruta no encontrada", status_code=404)
    except Exception as e:
        return error_response(f"Error al eliminar ruta: {str(e)}")
