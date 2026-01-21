from fastapi import APIRouter, status
from models.downtime_model import DowntimeModel
from config.database import downtimes_collection, trucks_collection
from schemas.downtime_scheme import downtime_helper
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo

from bson import ObjectId

router = APIRouter()


@router.post("/")
async def create_downtime(downtime: DowntimeModel):
    """
    Create a new downtime record
    Nueva estructura: Ya NO actualiza el array en coversheet,
    solo guarda la referencia coversheet_ref_id en el downtime
    """
    try:
        data = downtime.model_dump()
        
        # 🆕 Convertir coversheet_ref_id a ObjectId
        coversheet_ref_id = data.get("coversheet_ref_id")
        if coversheet_ref_id:
            data["coversheet_ref_id"] = ObjectId(coversheet_ref_id)
        
        # Convertir truck_id a ObjectId si existe
        truck_id = data.get("truck_id")
        if truck_id:
            data["truck_id"] = ObjectId(truck_id)
            
            # Obtener truckNumber para desnormalización
            truck_doc = await trucks_collection.find_one({"_id": data["truck_id"]})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
        
        # Asegurar que active está en True
        data["active"] = data.get("active", True)

        # Insertar el nuevo downtime
        new = await downtimes_collection.insert_one(data)
        created = await downtimes_collection.find_one({"_id": new.inserted_id})

        # ❌ Ya NO llamamos a add_entity_to_coversheet
        # El coversheet ya no mantiene arrays de IDs

        return success_response(
            downtime_helper(created), 
            msg="Downtime creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear downtime: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_downtimes():
    """Get all active downtimes"""
    try:
        # 🆕 Filtrar solo los activos
        downtimes = [
            downtime_helper(d) 
            async for d in downtimes_collection.find({"active": True})
        ]
        return success_response(downtimes, msg="Lista de downtimes obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener downtimes: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_downtime(id: str):
    """Get a single active downtime by ID"""
    try:
        downtime = await downtimes_collection.find_one({
            "_id": ObjectId(id),
            "active": True  # 🆕 Solo buscar activos
        })
        if downtime:
            return success_response(downtime_helper(downtime), msg="Downtime encontrada")
        return error_response(
            "Downtime no encontrada", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener downtime: {str(e)}")


@router.put("/{id}")
async def update_downtime(id: str, downtime: DowntimeModel):
    """Update an existing active downtime"""
    try:
        data = downtime.model_dump(exclude_unset=True)
        
        # 🆕 Prevenir actualización de campos sensibles
        if "coversheet_ref_id" in data:
            del data["coversheet_ref_id"]  # No permitir cambiar el padre
        if "active" in data:
            del data["active"]  # No permitir cambiar active a través de este endpoint
        
        # 🆕 Actualizar timestamp
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # Convertir truck_id a ObjectId si está siendo actualizado
        truck_id = data.get("truck_id")
        if truck_id:
            data["truck_id"] = ObjectId(truck_id)
            
            # Actualizar truckNumber desnormalizado
            truck_doc = await trucks_collection.find_one({"_id": data["truck_id"]})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        # 🆕 Solo actualizar si el downtime está activo
        res = await downtimes_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "Downtime no encontrada o no está activa", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await downtimes_collection.find_one({"_id": ObjectId(id)})
        return success_response(downtime_helper(updated), msg="Downtime actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar downtime: {str(e)}")


@router.delete("/{id}")
async def delete_downtime(id: str):
    """
    Soft delete a downtime by setting active=False
    ❌ Ya NO es un hard delete
    """
    try:
        # Verificar que el downtime existe y está activo
        downtime = await downtimes_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not downtime:
            return error_response(
                "Downtime no encontrada o ya fue eliminada", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 🆕 Soft delete: marcar como inactivo
        await downtimes_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="Downtime eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar downtime: {str(e)}")


@router.get("/by-coversheet/{coversheet_id}")
async def get_downtimes_by_coversheet(coversheet_id: str):
    """
    🆕 Nuevo endpoint: Obtener todos los downtimes de un coversheet específico
    Útil para queries desde el frontend
    """
    try:
        coversheet_oid = ObjectId(coversheet_id)
        
        downtimes = [
            downtime_helper(d)
            async for d in downtimes_collection.find({
                "coversheet_ref_id": coversheet_oid,
                "active": True
            })
        ]
        
        return success_response(
            downtimes, 
            msg=f"Downtimes del coversheet {coversheet_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener downtimes por coversheet: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )