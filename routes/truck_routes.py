from fastapi import APIRouter, HTTPException
from models.truck_model import TruckModel
from config.database import trucks_collection
from schemas.truck_scheme import truck_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_truck(truck: TruckModel):
    new = await trucks_collection.insert_one(truck.model_dump())
    created = await trucks_collection.find_one({"_id": new.inserted_id})
    return truck_helper(created)

@router.get("/")
async def get_all_trucks():
    return [truck_helper(truck) async for truck in trucks_collection.find()]

@router.get("/{id}")
async def get_truck(id: str):
    truck = await trucks_collection.find_one({"_id": ObjectId(id)})
    if truck:
        return truck_helper(truck)
    raise HTTPException(404, detail="Truck not found")

@router.put("/{id}")
async def update_truck(id: str, truck: TruckModel):
    await trucks_collection.update_one({"_id": ObjectId(id)}, {"$set": truck.model_dump()})
    updated = await trucks_collection.find_one({"_id": ObjectId(id)})
    return truck_helper(updated)

@router.delete("/{id}")
async def delete_truck(id: str):
    res = await trucks_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Truck deleted"}
    raise HTTPException(404, detail="Truck not found")
