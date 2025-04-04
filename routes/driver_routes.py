from fastapi import APIRouter, HTTPException
from models.driver_model import DriverModel
from config.database import drivers_collection
from schemas.driver_scheme import driver_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_driver(driver: DriverModel):
    new = await drivers_collection.insert_one(driver.dict())
    created = await drivers_collection.find_one({"_id": new.inserted_id})
    return driver_helper(created)

@router.get("/")
async def get_all_drivers():
    return [driver_helper(driver) async for driver in drivers_collection.find()]

@router.get("/{id}")
async def get_driver(id: str):
    driver = await drivers_collection.find_one({"_id": ObjectId(id)})
    if driver:
        return driver_helper(driver)
    raise HTTPException(404, detail="Driver not found")

@router.put("/{id}")
async def update_driver(id: str, driver: DriverModel):
    await drivers_collection.update_one({"_id": ObjectId(id)}, {"$set": driver.dict()})
    updated = await drivers_collection.find_one({"_id": ObjectId(id)})
    return driver_helper(updated)


@router.delete("/{id}")
async def delete_driver(id: str):
    res = await drivers_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Driver deleted"}
    raise HTTPException(404, detail="Driver not found")
