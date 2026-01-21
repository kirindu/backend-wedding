from fastapi import APIRouter, status, Depends
from models.coversheet_model import CoversheetModel
from config.database import coversheets_collection
from schemas.coversheet_scheme import coversheet_helper
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

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
    """
    Expands related data by querying child collections using coversheet_ref_id
    instead of using arrays in the coversheet document
    """
    try:
        coversheet_id = coversheet["_id"]
        
        # Query loads that reference this coversheet
        loads = [
            load_helper(doc) 
            async for doc in loads_collection.find({"coversheet_ref_id": coversheet_id})
        ]

        # Query downtimes that reference this coversheet
        downtimes = [
            downtime_helper(doc) 
            async for doc in downtimes_collection.find({"coversheet_ref_id": coversheet_id})
        ]

        # Query spare truck infos that reference this coversheet
        sparetrucks = [
            sparetruckinfo_helper(doc) 
            async for doc in sparetruckinfos_collection.find({"coversheet_ref_id": coversheet_id})
        ]

        # Get single relationships
        truck = await trucks_collection.find_one({"_id": coversheet["truck_id"]})
        route = await routes_collection.find_one({"_id": coversheet["route_id"]})
        driver = await drivers_collection.find_one({"_id": coversheet["driver_id"]})

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
        return error_response(
            f"Error al expandir datos relacionados: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/with-details")
async def get_all_coversheets_with_details():
    """Get all active coversheets with related data expanded"""
    try:
        # Only get active coversheets
        coversheets = [
            doc async for doc in coversheets_collection.find({"active": True})
        ]
        result = [await expand_related_data(c) for c in coversheets]
        return success_response(result, msg="Coversheets con detalles obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets con detalles: {str(e)}")


@router.get("/with-details/{id}")
async def get_coversheet_with_details(id: str):
    """Get a single active coversheet with related data expanded"""
    try:
        coversheet = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrada", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        return success_response(await expand_related_data(coversheet))
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.post("/")
async def create_coversheet(coversheet: CoversheetModel):
    """Create a new coversheet"""
    try:
        data = coversheet.model_dump()
        
        # Convert string IDs to ObjectId
        data["truck_id"] = ObjectId(data["truck_id"])
        data["route_id"] = ObjectId(data["route_id"])
        data["driver_id"] = ObjectId(data["driver_id"])

        # Fetch denormalized data from related collections
        truck_doc = await trucks_collection.find_one({"_id": data["truck_id"]})
        if truck_doc and truck_doc.get("truckNumber"):
            data["truckNumber"] = truck_doc["truckNumber"]

        route_doc = await routes_collection.find_one({"_id": data["route_id"]})
        if route_doc and route_doc.get("routeNumber"):
            data["routeNumber"] = route_doc["routeNumber"]

        driver_doc = await drivers_collection.find_one({"_id": data["driver_id"]})
        if driver_doc and driver_doc.get("name"):
            data["driverName"] = driver_doc["name"]

        # Ensure active is set
        data["active"] = data.get("active", True)

        # Insert the new coversheet
        new = await coversheets_collection.insert_one(data)
        created = await coversheets_collection.find_one({"_id": new.inserted_id})
        return success_response(
            coversheet_helper(created), 
            msg="Coversheet creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear coversheet: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_coversheets():
    """Get all active coversheets"""
    try:
        coversheets = [
            coversheet_helper(c) 
            async for c in coversheets_collection.find({"active": True})
        ]
        return success_response(coversheets, msg="Coversheets obtenidas")
    except Exception as e:
        return error_response(f"Error al obtener coversheets: {str(e)}")


@router.get("/by-date/{date}")
async def get_coversheets_by_date(date: str):
    """Get active coversheets for a specific date"""
    try:
        # Parse date string
        try:
            query_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return error_response(
                "Formato de fecha inválido. Usa YYYY-MM-DD", 
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Create date range for the full day
        start = datetime(query_date.year, query_date.month, query_date.day)
        end = start + timedelta(days=1)

        # Find active coversheets in date range
        coversheets = [
            coversheet_helper(c)
            async for c in coversheets_collection.find({
                "date": {"$gte": start, "$lt": end},
                "active": True
            })
        ]

        return success_response(
            coversheets, 
            msg=f"Coversheets del día {date} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener coversheets por fecha: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_coversheet(id: str):
    """Get a single active coversheet"""
    try:
        c = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if c:
            return success_response(coversheet_helper(c))
        return error_response(
            "Coversheet no encontrada", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoversheetModel):
    """Update an existing active coversheet"""
    try:
        data = coversheet.model_dump(exclude_unset=True)

        # Prevent updating the date field
        if "date" in data:
            del data["date"]
        
        # Prevent updating the active field through this endpoint
        if "active" in data:
            del data["active"]

        # Update timestamp
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        # Convert string IDs to ObjectId if they're being updated
        if "truck_id" in data:
            data["truck_id"] = ObjectId(data["truck_id"])
            truck_doc = await trucks_collection.find_one({"_id": data["truck_id"]})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        if "route_id" in data:
            data["route_id"] = ObjectId(data["route_id"])
            route_doc = await routes_collection.find_one({"_id": data["route_id"]})
            if route_doc and route_doc.get("routeNumber"):
                data["routeNumber"] = route_doc["routeNumber"]

        if "driver_id" in data:
            data["driver_id"] = ObjectId(data["driver_id"])
            driver_doc = await drivers_collection.find_one({"_id": data["driver_id"]})
            if driver_doc and driver_doc.get("name"):
                data["driverName"] = driver_doc["name"]

        # Update only if the coversheet is active
        res = await coversheets_collection.update_one(
            {"_id": ObjectId(id), "active": True}, 
            {"$set": data}
        )
        
        if res.matched_count == 0:
            return error_response(
                "Coversheet no encontrada o no está activa", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await coversheets_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            coversheet_helper(updated), 
            msg="Coversheet actualizada exitosamente"
        )
    except Exception as e:
        return error_response(f"Error al actualizar coversheet: {str(e)}")


@router.delete("/{id}")
async def delete_coversheet(id: str):
    """
    Soft delete a coversheet by setting active=False
    Also soft deletes all related child records
    """
    try:
        coversheet_oid = ObjectId(id)
        
        # Check if coversheet exists and is active
        coversheet = await coversheets_collection.find_one({
            "_id": coversheet_oid,
            "active": True
        })
        
        if not coversheet:
            return error_response(
                "Coversheet no encontrada o ya fue eliminada", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Soft delete the coversheet
        await coversheets_collection.update_one(
            {"_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        # Soft delete all related loads
        await loads_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        # Soft delete all related downtimes
        await downtimes_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        # Soft delete all related spare truck infos
        await sparetruckinfos_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="Coversheet eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar coversheet: {str(e)}")


@router.get("/{id}/sparetruckinfo")
async def get_sparetruckinfo_by_coversheet(id: str):
    """Get all spare truck infos that reference a specific coversheet"""
    try:
        coversheet_oid = ObjectId(id)
        
        # Verify coversheet exists and is active
        coversheet = await coversheets_collection.find_one({
            "_id": coversheet_oid,
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrado", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Query spare truck infos by coversheet reference
        results = [
            sparetruckinfo_helper(doc)
            async for doc in sparetruckinfos_collection.find({
                "coversheet_ref_id": coversheet_oid
            })
        ]

        return success_response(results, msg="SpareTruckInfos obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")


@router.get("/{id}/downtime")
async def get_downtime_by_coversheet(id: str):
    """Get all downtimes that reference a specific coversheet"""
    try:
        coversheet_oid = ObjectId(id)
        
        # Verify coversheet exists and is active
        coversheet = await coversheets_collection.find_one({
            "_id": coversheet_oid,
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrado", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Query downtimes by coversheet reference
        results = [
            downtime_helper(doc)
            async for doc in downtimes_collection.find({
                "coversheet_ref_id": coversheet_oid
            })
        ]

        return success_response(results, msg="Downtimes obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener Downtimes: {str(e)}")


@router.get("/{id}/load")
async def get_load_by_coversheet(id: str):
    """Get all loads that reference a specific coversheet"""
    try:
        coversheet_oid = ObjectId(id)
        
        # Verify coversheet exists and is active
        coversheet = await coversheets_collection.find_one({
            "_id": coversheet_oid,
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrado", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Query loads by coversheet reference
        results = [
            load_helper(doc)
            async for doc in loads_collection.find({
                "coversheet_ref_id": coversheet_oid
            })
        ]

        return success_response(results, msg="Loads obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener Loads: {str(e)}")