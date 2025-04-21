from fastapi import APIRouter, HTTPException, status
from models.downtime_model import DowntimeModel
from config.database import downtimes_collection
from schemas.downtime_scheme import downtime_helper
from utils.coversheet_updater import add_entity_to_coversheet

from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_downtime(downtime: DowntimeModel):
    
    data = downtime.model_dump()
    coversheet_id = data.pop("coversheet_id")  # extrae y remueve coversheet_id del dict
    new = await downtimes_collection.insert_one(data)
    created = await downtimes_collection.find_one({"_id": new.inserted_id})
    
    await add_entity_to_coversheet(coversheet_id, "downtime_id", str(new.inserted_id))

    return downtime_helper(created)

@router.get("/")
async def get_all_downtimes():
    return [downtime_helper(downtime) async for downtime in downtimes_collection.find()]

@router.get("/{id}")
async def get_downtime(id: str):
    downtime = await downtimes_collection.find_one({"_id": ObjectId(id)})
    if downtime:
        return downtime_helper(downtime)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Downtime not found")

@router.put("/{id}")
async def update_downtime(id: str, downtime: DowntimeModel):
    res = await downtimes_collection.update_one({"_id": ObjectId(id)}, {"$set": downtime.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Downtime not found")
    updated = await downtimes_collection.find_one({"_id": ObjectId(id)})
    return downtime_helper(updated)


@router.delete("/{id}")
async def delete_downtime(id: str):
    res = await downtimes_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Downtime deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Downtime not found")
