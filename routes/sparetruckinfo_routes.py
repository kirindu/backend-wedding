from fastapi import APIRouter, HTTPException, status
from models.sparetruckinfo_model import SpareTruckInfoModel
from config.database import sparetruckinfos_collection
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_sparetruckinfo(sparetruckinfo: SpareTruckInfoModel):
    new = await sparetruckinfos_collection.insert_one(sparetruckinfo.model_dump())
    created = await sparetruckinfos_collection.find_one({"_id": new.inserted_id})
    return sparetruckinfo_helper(created)

@router.get("/")
async def get_all_sparetruckinfos():
    return [sparetruckinfo_helper(sparetruckinfo) async for sparetruckinfo in sparetruckinfos_collection.find()]

@router.get("/{id}")
async def get_sparetruckinfo(id: str):
    sparetruckinfo = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
    if sparetruckinfo:
        return sparetruckinfo_helper(sparetruckinfo)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sparetruckinfo not found")

@router.put("/{id}")
async def update_sparetruckinfo(id: str, sparetruckinfo: SpareTruckInfoModel):
    res = await sparetruckinfos_collection.update_one({"_id": ObjectId(id)}, {"$set": sparetruckinfo.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sparetruckinfo not found")
    updated = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
    return sparetruckinfo_helper(updated)


@router.delete("/{id}")
async def delete_sparetruckinfo(id: str):
    res = await sparetruckinfos_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Sparetruckinfo deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sparetruckinfo not found")
