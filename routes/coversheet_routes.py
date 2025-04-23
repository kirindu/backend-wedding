from fastapi import APIRouter, HTTPException, status,Depends
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from config.dependencies import get_current_user



from schemas.load_scheme import load_helper
from schemas.downtime_scheme import downtime_helper
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from schemas.truck_scheme import truck_helper
from schemas.route_scheme import route_helper
from schemas.driver_scheme import driver_helper

from config.database import (
    loads_collection,
    downtimes_collection,
    sparetruckinfos_collection,
    trucks_collection,
    routes_collection,
    drivers_collection
)

from bson import ObjectId

async def expand_related_data(coversheet):
    # Expandir Loads
    loads = []
    for load_id in coversheet.get("load_id", []):
        load = await loads_collection.find_one({"_id": ObjectId(load_id)})
        if load:
            loads.append(load_helper(load))

    # Expandir Downtime
    downtimes = []
    for dt_id in coversheet.get("downtime_id", []):
        dt = await downtimes_collection.find_one({"_id": ObjectId(dt_id)})
        if dt:
            downtimes.append(downtime_helper(dt))

    # Expandir SpareTruckInfo
    sparetrucks = []
    for sp_id in coversheet.get("spareTruckInfo_id", []):
        st = await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)})
        if st:
            sparetrucks.append(sparetruckinfo_helper(st))

    # Expandir referencias únicas
    truck = await trucks_collection.find_one({"_id": ObjectId(coversheet["truck_id"])})
    route = await routes_collection.find_one({"_id": ObjectId(coversheet["route_id"])})
    driver = await drivers_collection.find_one({"_id": ObjectId(coversheet["driver_id"])})

    return {
        **coversheet_helper(coversheet),
        "loads": loads,
        "downtimes": downtimes,
        "spareTruckInfos": sparetrucks,
        "truck": truck_helper(truck) if truck else None,
        "route": route_helper(route) if route else None,
        "driver": driver_helper(driver) if driver else None
    }


router = APIRouter()

@router.get("/with-details")
async def get_all_coversheets_with_details():
    coversheets = [doc async for doc in coversheets_collection.find()]
    return [await expand_related_data(c) for c in coversheets]

@router.get("/with-details/{id}")
async def get_coversheet_with_details(id: str):
    coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
    if not coversheet:
        raise HTTPException(status_code=404, detail="Coversheet not found")
    return await expand_related_data(coversheet)



@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    new = await coversheets_collection.insert_one(coversheet.model_dump())
    created = await coversheets_collection.find_one({"_id": new.inserted_id})
    return coversheet_helper(created)


# Uncomment the following lines if you want to restrict access to the create_coversheet endpoint
# @router.post("/")
# async def create_coversheet(coversheet: CoversheetModel, current_user: dict = Depends(get_current_user)):
#     if current_user.get("rol") != "Admin":
#         raise HTTPException(status_code=403, detail="No tienes permiso para crear Coversheets")

#     new = await coversheets_collection.insert_one(coversheet.model_dump())
#     created = await coversheets_collection.find_one({"_id": new.inserted_id})
#     return coversheet_helper(created)



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
