from fastapi import APIRouter, HTTPException, status
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    new = await coversheets_collection.insert_one(coversheet.model_dump())
    created = await coversheets_collection.find_one({"_id": new.inserted_id})
    return coversheet_helper(created)

@router.get("/")
async def get_all_coversheets():
    return [coversheet_helper(c) async for c in coversheets_collection.find()]

@router.get("/{id}")
async def get_coversheet(id: str):
    c = await coversheets_collection.find_one({"_id": ObjectId(id)})
    if c:
        return coversheet_helper(c)
    raise HTTPException(404, detail="Coversheet not found")

@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
   res = await coversheets_collection.update_one({"_id": ObjectId(id)}, {"$set": coversheet.model_dump()})
   if res.matched_count == 0:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CoverSheet not found")
   updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
   return coversheet_helper(updated)

@router.delete("/{id}")
async def delete_coversheet(id: str):
    res = await coversheets_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Coversheet deleted"}
    raise HTTPException(404, detail="Coversheet not found")
