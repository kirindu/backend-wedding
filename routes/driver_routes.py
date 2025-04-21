from fastapi import APIRouter, HTTPException, status, Form
from models.driver_model import DriverModel
from config.database import drivers_collection
from schemas.driver_scheme import driver_helper
from bson import ObjectId

router = APIRouter()

@router.post("/login")
async def driver_login(email: str = Form(...), password: str = Form(...)):
    driver = await drivers_collection.find_one({"email": email})
    if not driver or driver["password"] != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    
    return {
        "msg": "Login exitoso",
        "driver": {
            "id": str(driver["_id"]),
            "name": driver["name"],
            "email": driver["email"],
            "rol": driver["rol"]
        }
    }

@router.post("/")
async def create_driver(driver: DriverModel):
    new = await drivers_collection.insert_one(driver.model_dump())
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
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")

@router.put("/{id}")
async def update_driver(id: str, driver: DriverModel):
    res = await drivers_collection.update_one({"_id": ObjectId(id)}, {"$set": driver.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
    updated = await drivers_collection.find_one({"_id": ObjectId(id)})
    return driver_helper(updated)


@router.delete("/{id}")
async def delete_driver(id: str):
    res = await drivers_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Driver deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver not found")
