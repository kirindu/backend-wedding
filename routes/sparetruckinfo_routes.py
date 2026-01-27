from fastapi import APIRouter, status
from models.sparetruckinfo_model import SpareTruckInfoModel
from config.database import sparetruckinfos_collection, routes_collection
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

router = APIRouter()


@router.post("/")
async def create_sparetruckinfo(sparetruckinfo: SpareTruckInfoModel):
    """
    Create a new spare truck info record
    Nueva estructura: Ya NO actualiza el array en coversheet,
    solo guarda la referencia coversheet_ref_id en el sparetruckinfo
    """
    try:
        data = sparetruckinfo.model_dump()
        
        # 🆕 Convertir coversheet_ref_id a ObjectId
        coversheet_ref_id = data.get("coversheet_ref_id")
        if coversheet_ref_id:
            data["coversheet_ref_id"] = ObjectId(coversheet_ref_id)
        
        # Convertir route_id a ObjectId y obtener routeNumber
        route_id = data.get("route_id")
        if route_id:
            data["route_id"] = ObjectId(route_id)
            
            # Obtener routeNumber para desnormalización
            route_doc = await routes_collection.find_one({"_id": data["route_id"]})
            if route_doc and route_doc.get("routeNumber"):
                data["routeNumber"] = route_doc["routeNumber"]
        
        # Asegurar que active está en True
        data["active"] = data.get("active", True)

        # Insertar el nuevo SpareTruckInfo
        new = await sparetruckinfos_collection.insert_one(data)
        created = await sparetruckinfos_collection.find_one({"_id": new.inserted_id})

        # ❌ Ya NO llamamos a add_entity_to_coversheet
        # El coversheet ya no mantiene arrays de IDs

        return success_response(
            sparetruckinfo_helper(created), 
            msg="SpareTruckInfo creado exitosamente"
        )

    except Exception as e:
        return error_response(
            f"Error al crear SpareTruckInfo: {str(e)}", 
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_sparetruckinfos():
    """Get all active spare truck infos"""
    try:
        # 🆕 Filtrar solo los activos
        result = [
            sparetruckinfo_helper(sp) 
            async for sp in sparetruckinfos_collection.find({"active": True})
        ]
        return success_response(result, msg="Lista de SpareTruckInfos obtenida")
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")


@router.get("/{id}")
async def get_sparetruckinfo(id: str):
    """Get a single active spare truck info by ID"""
    try:
        sparetruckinfo = await sparetruckinfos_collection.find_one({
            "_id": ObjectId(id),
            "active": True  # 🆕 Solo buscar activos
        })
        if sparetruckinfo:
            return success_response(
                sparetruckinfo_helper(sparetruckinfo), 
                msg="SpareTruckInfo encontrado"
            )
        return error_response(
            "SpareTruckInfo no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfo: {str(e)}")


@router.put("/{id}")
async def update_sparetruckinfo(id: str, sparetruckinfo: SpareTruckInfoModel):
    """Update an existing active spare truck info"""
    try:
        data = sparetruckinfo.model_dump(exclude_unset=True)
        
        # 🆕 Prevenir actualización de campos sensibles
        if "coversheet_ref_id" in data:
            del data["coversheet_ref_id"]  # No permitir cambiar el padre
        if "active" in data:
            del data["active"]  # No permitir cambiar active a través de este endpoint
        
        # 🆕 Actualizar timestamp
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))
        
        # Convertir route_id a ObjectId si está siendo actualizado
        route_id = data.get("route_id")
        if route_id:
            data["route_id"] = ObjectId(route_id)
            
            # Actualizar routeNumber desnormalizado
            route_doc = await routes_collection.find_one({"_id": data["route_id"]})
            if route_doc and route_doc.get("routeNumber"):
                data["routeNumber"] = route_doc["routeNumber"]

        # 🆕 Solo actualizar si el sparetruckinfo está activo
        res = await sparetruckinfos_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "SpareTruckInfo no encontrado o no está activo", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            sparetruckinfo_helper(updated), 
            msg="SpareTruckInfo actualizado"
        )

    except Exception as e:
        return error_response(f"Error al actualizar SpareTruckInfo: {str(e)}")


@router.delete("/{id}")
async def delete_sparetruckinfo(id: str):
    """
    Soft delete a spare truck info by setting active=False
    ❌ Ya NO es un hard delete
    """
    try:
        # Verificar que el sparetruckinfo existe y está activo
        sparetruckinfo = await sparetruckinfos_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not sparetruckinfo:
            return error_response(
                "SpareTruckInfo no encontrado o ya fue eliminado", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 🆕 Soft delete: marcar como inactivo
        await sparetruckinfos_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="SpareTruckInfo eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar SpareTruckInfo: {str(e)}")


@router.get("/by-coversheet/{coversheet_id}")
async def get_sparetruckinfos_by_coversheet(coversheet_id: str):
    """
    🆕 Nuevo endpoint: Obtener todos los spare truck infos de un coversheet específico
    Útil para queries desde el frontend
    """
    try:
        coversheet_oid = ObjectId(coversheet_id)
        
        sparetruckinfos = [
            sparetruckinfo_helper(sp)
            async for sp in sparetruckinfos_collection.find({
                "coversheet_ref_id": coversheet_oid,
                "active": True
            })
        ]
        
        return success_response(
            sparetruckinfos, 
            msg=f"SpareTruckInfos del coversheet {coversheet_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener SpareTruckInfos por coversheet: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )