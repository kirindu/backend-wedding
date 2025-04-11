from fastapi import APIRouter, HTTPException
from models.route_model import RouteModel
from config.database import routes_collection
from schemas.route_scheme import route_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_route(route: RouteModel):
    new = await routes_collection.insert_one(route.model_dump())
    created = await routes_collection.find_one({"_id": new.inserted_id})
    return route_helper(created)

@router.get("/")
async def get_all_routes():
    return [route_helper(route) async for route in routes_collection.find()]

@router.get("/{id}")
async def get_route(id: str):
    route = await routes_collection.find_one({"_id": ObjectId(id)})
    if route:
        return route_helper(route)
    raise HTTPException(404, detail="Route not found")

@router.put("/{id}")
async def update_route(id: str, route: RouteModel):
    await routes_collection.update_one({"_id": ObjectId(id)}, {"$set": route.model_dump()})
    updated = await routes_collection.find_one({"_id": ObjectId(id)})
    return route_helper(updated)

@router.delete("/{id}")
async def delete_route(id: str):
    res = await routes_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Route deleted"}
    raise HTTPException(404, detail="Route not found")
