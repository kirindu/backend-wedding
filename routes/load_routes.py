from fastapi import APIRouter, HTTPException, status
from models.load_model import LoadModel
from config.database import loads_collection
from schemas.load_scheme import load_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_load(load: LoadModel):
    new = await loads_collection.insert_one(load.model_dump())
    created = await loads_collection.find_one({"_id": new.inserted_id})
    return load_helper(created)

@router.get("/")
async def get_all_loads():
    return [load_helper(load) async for load in loads_collection.find()]

@router.get("/{id}")
async def get_load(id: str):
    load = await loads_collection.find_one({"_id": ObjectId(id)})
    if load:
        return load_helper(load)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")

@router.put("/{id}")
async def update_load(id: str, load: LoadModel):
    res = await loads_collection.update_one({"_id": ObjectId(id)}, {"$set": load.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")
    updated = await loads_collection.find_one({"_id": ObjectId(id)})
    return load_helper(updated)


@router.delete("/{id}")
async def delete_load(id: str):
    res = await loads_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Load deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")
