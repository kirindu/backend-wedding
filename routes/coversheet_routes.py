from fastapi import APIRouter, status, Depends
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response

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

router = APIRouter()

async def expand_related_data(coversheet):
    try:
        loads = [load_helper(await loads_collection.find_one({"_id": ObjectId(load_id)}))
                 for load_id in coversheet.get("load_id", []) if await loads_collection.find_one({"_id": ObjectId(load_id)})]

        downtimes = [downtime_helper(await downtimes_collection.find_one({"_id": ObjectId(dt_id)}))
                     for dt_id in coversheet.get("downtime_id", []) if await downtimes_collection.find_one({"_id": ObjectId(dt_id)})]

        sparetrucks = [sparetruckinfo_helper(await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)}))
                       for sp_id in coversheet.get("spareTruckInfo_id", []) if await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)})]

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
    except Exception as e:
        return error_response(f"Error al expandir datos relacionados: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/with-details")
async def get_all_coversheets_with_details():
    try:
        coversheets = [doc async for doc in coversheets_collection.find()]
        result = [await expand_related_data(c) for c in coversheets]
        return success_response(result, msg="Coversheets con detalles obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets con detalles: {str(e)}")


@router.get("/with-details/{id}")
async def get_coversheet_with_details(id: str):
    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
        return success_response(await expand_related_data(coversheet))
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    try:
        new = await coversheets_collection.insert_one(coversheet.model_dump())
        created = await coversheets_collection.find_one({"_id": new.inserted_id})
        return success_response(coversheet_helper(created), msg="Coversheet creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear coversheet: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_coversheets():
    try:
        coversheets = [coversheet_helper(c) async for c in coversheets_collection.find()]
        return success_response(coversheets, msg="Coversheets obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets: {str(e)}")


@router.get("/{id}")
async def get_coversheet(id: str):
    try:
        c = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if c:
            return success_response(coversheet_helper(c))
        return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
    try:
        res = await coversheets_collection.update_one({"_id": ObjectId(id)}, {"$set": coversheet.model_dump()})
        if res.matched_count == 0:
            return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
        updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
        return success_response(coversheet_helper(updated), msg="Coversheet actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar coversheet: {str(e)}")


@router.delete("/{id}")
async def delete_coversheet(id: str):
    try:
        res = await coversheets_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Coversheet eliminada")
        return error_response("Coversheet no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar coversheet: {str(e)}")

@router.get("/{id}/sparetruckinfo")
async def get_sparetruckinfo_by_coversheet(id: str):
    from config.database import sparetruckinfos_collection
    from schemas.sparetruckinfo_scheme import sparetruckinfo_helper

    try:
        coversheet = await coversheets_collection.find_one({"_id": ObjectId(id)})
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        spare_ids = coversheet.get("spareTruckInfo_id", [])
        if not spare_ids:
            return success_response([], msg="No hay SpareTruckInfos asociados")

        results = []
        for sp_id in spare_ids:
            doc = await sparetruckinfos_collection.find_one({"_id": ObjectId(sp_id)})
            if doc:
                results.append(sparetruckinfo_helper(doc))

        return success_response(results, msg="SpareTruckInfos obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")
