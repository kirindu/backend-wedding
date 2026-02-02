from zoneinfo import ZoneInfo
from fastapi import APIRouter, status, Depends
from models.sparetruckinfo_model import SpareTruckInfoModel
from config.database import sparetruckinfos_collection, routes_collection, trucks_collection, coversheets_collection
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from utils.response_helper import success_response, error_response
from config.dependencies import get_current_user
from datetime import datetime
from bson import ObjectId

router = APIRouter()


# ===========================
# FUNCIÓN HELPER
# ===========================

async def fetch_and_embed_related_data(data: dict) -> dict:
    """
    Helper para traer y embeber datos relacionados (desnormalización).
    Esto mejora el performance al evitar JOINs posteriores.
    """
    # 🚗 Fetch truckNumber si hay spareTruckNumber (campo de texto libre)
    # En tu caso, el spareTruckNumber es un string que el usuario ingresa
    # No necesita lookup, pero si tuvieras truck_id, aquí lo harías
    
    # 🚛 Fetch routeNumber from routes_collection
    if "route_id" in data and data["route_id"]:
        route_doc = await routes_collection.find_one({"_id": data["route_id"]})
        if route_doc and route_doc.get("routeNumber"):
            data["routeNumber"] = route_doc["routeNumber"]
    
    return data


# ===========================
# RUTAS
# ===========================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sparetruckinfo(sparetruckinfo: SpareTruckInfoModel):
    """
    Crea un nuevo spare truck info.
    
    Requiere coversheet_ref_id para vincular al coversheet padre.
    Los campos de auditoría se generan automáticamente.
    """
    try:
        data = sparetruckinfo.model_dump()
        
        # ✅ PASO 1: Proteger campos de auditoría
        # Remover si vienen en el request (no confiar en el cliente)
        data.pop("createdAt", None)
        data.pop("updatedAt", None)
        data.pop("active", None)  # Siempre debe ser True al crear
        
        # ✅ PASO 2: Validar y convertir coversheet_ref_id
        coversheet_ref_id = data.get("coversheet_ref_id")
        if not coversheet_ref_id:
            return error_response(
                "coversheet_ref_id es requerido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if not ObjectId.is_valid(coversheet_ref_id):
            return error_response(
                "coversheet_ref_id inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        data["coversheet_ref_id"] = ObjectId(coversheet_ref_id)
        
        # Verificar que el coversheet existe y está activo
        coversheet = await coversheets_collection.find_one({
            "_id": data["coversheet_ref_id"],
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrado o no está activo",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ PASO 3: Convertir route_id a ObjectId si existe
        if data.get("route_id"):
            if not ObjectId.is_valid(data["route_id"]):
                return error_response(
                    "route_id inválido",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            data["route_id"] = ObjectId(data["route_id"])
        
        # ✅ PASO 4: Campos de auditoría
        tz = ZoneInfo("America/Denver")
        data["createdAt"] = datetime.now(tz)
        data["updatedAt"] = None
        data["active"] = True
        
        # ✅ PASO 5: Desnormalización (fetch nombres relacionados)
        data = await fetch_and_embed_related_data(data)
        
        # ✅ PASO 6: Insertar en la base de datos
        new = await sparetruckinfos_collection.insert_one(data)
        created = await sparetruckinfos_collection.find_one({"_id": new.inserted_id})
        
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
async def get_all_sparetruckinfos(
    active_only: bool = True,
    coversheet_id: str = None
):
    """
    Obtiene todos los spare truck infos.
    
    Parámetros:
    - active_only: Si es True, solo devuelve registros activos (default: True)
    - coversheet_id: Filtrar por coversheet específico (opcional)
    
    Ejemplos:
    - GET /api/sparetruckinfo/ → Todos los activos
    - GET /api/sparetruckinfo/?active_only=false → Todos (incluyendo eliminados)
    - GET /api/sparetruckinfo/?coversheet_id=ABC123 → Del coversheet específico
    """
    try:
        # Construir query
        query = {}
        
        if active_only:
            query["active"] = True
        
        if coversheet_id:
            if not ObjectId.is_valid(coversheet_id):
                return error_response(
                    "coversheet_id inválido",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            query["coversheet_ref_id"] = ObjectId(coversheet_id)
        
        # Obtener documentos
        cursor = sparetruckinfos_collection.find(query)
        docs = await cursor.to_list(length=None)
        result = [sparetruckinfo_helper(sp) for sp in docs]
        
        return success_response(result, msg="Lista de SpareTruckInfos obtenida")
        
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfos: {str(e)}")


@router.get("/{id}")
async def get_sparetruckinfo(id: str, include_inactive: bool = False):
    """
    Obtiene un spare truck info por ID.
    
    Parámetros:
    - id: ID del spare truck info
    - include_inactive: Si es True, permite obtener registros inactivos (default: False)
    """
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(id):
            return error_response(
                "ID inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Construir query
        query = {"_id": ObjectId(id)}
        if not include_inactive:
            query["active"] = True
        
        sparetruckinfo = await sparetruckinfos_collection.find_one(query)
        
        if sparetruckinfo:
            return success_response(
                sparetruckinfo_helper(sparetruckinfo),
                msg="SpareTruckInfo encontrado"
            )
        
        return error_response(
            "SpareTruckInfo no encontrado o está inactivo",
            status_code=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        return error_response(f"Error al obtener SpareTruckInfo: {str(e)}")


@router.put("/{id}")
async def update_sparetruckinfo(id: str, sparetruckinfo: SpareTruckInfoModel):
    """
    Actualiza un spare truck info existente.
    
    No permite actualizar: coversheet_ref_id, active, createdAt
    Actualiza automáticamente: updatedAt
    """
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(id):
            return error_response(
                "ID inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Convertir modelo a dict (solo campos enviados)
        data = sparetruckinfo.model_dump(exclude_unset=True)
        
        # ✅ PASO 1: Proteger campos que NO deben cambiar
        data.pop("createdAt", None)
        data.pop("coversheet_ref_id", None)  # No permitir cambiar el padre
        data.pop("active", None)  # No permitir cambiar active
        
        # Si no hay datos para actualizar, retornar error
        if not data:
            return error_response(
                "No se proporcionaron campos para actualizar",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # ✅ PASO 2: Actualizar timestamp
        tz = ZoneInfo("America/Denver")
        data["updatedAt"] = datetime.now(tz)
        
        # ✅ PASO 3: Convertir route_id a ObjectId si está siendo actualizado
        if "route_id" in data and data["route_id"]:
            if not ObjectId.is_valid(data["route_id"]):
                return error_response(
                    "route_id inválido",
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            data["route_id"] = ObjectId(data["route_id"])
        
        # ✅ PASO 4: Desnormalización
        data = await fetch_and_embed_related_data(data)
        
        # ✅ PASO 5: Actualizar solo si está activo
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
            msg="SpareTruckInfo actualizado exitosamente"
        )
        
    except Exception as e:
        return error_response(f"Error al actualizar SpareTruckInfo: {str(e)}")


@router.delete("/{id}")
async def delete_sparetruckinfo(id: str):
    """
    Soft delete: Marca el spare truck info como inactivo.
    
    El registro NO se elimina físicamente, solo se marca como active=False.
    Esto preserva el historial.
    """
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(id):
            return error_response(
                "ID inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que existe y está activo
        existing = await sparetruckinfos_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not existing:
            return error_response(
                "SpareTruckInfo no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ Soft delete: marcar como inactivo
        tz = ZoneInfo("America/Denver")
        await sparetruckinfos_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(tz)
                }
            }
        )
        
        return success_response(
            {"id": id},
            msg="SpareTruckInfo eliminado (soft delete)"
        )
        
    except Exception as e:
        return error_response(f"Error al eliminar SpareTruckInfo: {str(e)}")


@router.delete("/{id}/permanent")
async def permanent_delete_sparetruckinfo(id: str, current_user: str = Depends(get_current_user)):
    """
    ⚠️ HARD DELETE: Elimina permanentemente el spare truck info.
    
    Esta operación es IRREVERSIBLE.
    Usar con precaución. Para eliminación normal, usar DELETE /{id} (soft delete).
    Requiere autenticación de usuario.
    """
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(id):
            return error_response(
                "ID inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que existe (sin importar si está activo o no)
        existing = await sparetruckinfos_collection.find_one({"_id": ObjectId(id)})
        if not existing:
            return error_response(
                "SpareTruckInfo no encontrado",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ Hard delete: eliminar físicamente
        result = await sparetruckinfos_collection.delete_one({"_id": ObjectId(id)})
        
        if result.deleted_count == 1:
            return success_response(
                {"id": id},
                msg="SpareTruckInfo eliminado permanentemente"
            )
        else:
            return error_response(
                "No se pudo eliminar el SpareTruckInfo",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        return error_response(f"Error al eliminar permanentemente: {str(e)}")


@router.get("/by-coversheet/{coversheet_id}")
async def get_sparetruckinfos_by_coversheet(coversheet_id: str, include_inactive: bool = False):
    """
    Obtiene todos los spare truck infos de un coversheet específico.
    
    Parámetros:
    - coversheet_id: ID del coversheet
    - include_inactive: Si es True, incluye registros inactivos (default: False)
    
    Ejemplos:
    - GET /api/sparetruckinfo/by-coversheet/ABC123
    - GET /api/sparetruckinfo/by-coversheet/ABC123?include_inactive=true
    """
    try:
        # Validar ObjectId
        if not ObjectId.is_valid(coversheet_id):
            return error_response(
                "coversheet_id inválido",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        coversheet_oid = ObjectId(coversheet_id)
        
        # Verificar que el coversheet existe y está activo
        coversheet = await coversheets_collection.find_one({
            "_id": coversheet_oid,
            "active": True
        })
        if not coversheet:
            return error_response(
                "Coversheet no encontrado o no está activo",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Construir query
        query = {"coversheet_ref_id": coversheet_oid}
        if not include_inactive:
            query["active"] = True
        
        # Obtener documentos
        cursor = sparetruckinfos_collection.find(query)
        docs = await cursor.to_list(length=None)
        sparetruckinfos = [sparetruckinfo_helper(sp) for sp in docs]
        
        return success_response(
            sparetruckinfos,
            msg=f"SpareTruckInfos del coversheet {coversheet_id} obtenidos"
        )
        
    except Exception as e:
        return error_response(
            f"Error al obtener SpareTruckInfos por coversheet: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )