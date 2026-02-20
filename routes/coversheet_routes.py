from zoneinfo import ZoneInfo
from fastapi import APIRouter, status, Depends
from models.coversheet_model import CoverSheetModel
from config.database import coversheets_collection
from schemas.incidentdetail_scheme import coversheet_helper
from config.dependencies import get_current_user
from utils.response_helper import success_response, error_response
from datetime import datetime, timedelta
from bson import ObjectId

# Importación de Helpers de otras colecciones
from schemas.load_scheme import load_helper
from schemas.downtime_scheme import downtime_helper
from schemas.sparetruckinfo_scheme import sparetruckinfo_helper
from schemas.truck_scheme import truck_helper
from schemas.route_scheme import route_helper
from schemas.employee_scheme import driver_helper

# Importación de Colecciones
from config.database import (
    loads_collection,
    downtimes_collection,
    sparetruckinfos_collection,
    trucks_collection,
    routes_collection,
    drivers_collection
)

router = APIRouter()


# ===========================
# FUNCIONES HELPER
# ===========================

async def expand_related_data_from_doc(doc):
    """
    Expande datos relacionados desde el documento MongoDB original.
    Usa referencia inversa (coversheet_ref_id en las colecciones hijas).
    """
    try:
        c_id = doc["_id"]  # Ya es ObjectId
        
        # Búsquedas directas por referencia inversa
        loads_cursor = loads_collection.find({"coversheet_ref_id": c_id, "active": True})
        downtimes_cursor = downtimes_collection.find({"coversheet_ref_id": c_id, "active": True})
        spares_cursor = sparetruckinfos_collection.find({"coversheet_ref_id": c_id, "active": True})
        
        # Convertir el coversheet primero
        coversheet_dict = coversheet_helper(doc)
        
        # Agregar las relaciones
        coversheet_dict["loads"] = [load_helper(d) for d in await loads_cursor.to_list(length=None)]
        coversheet_dict["downtimes"] = [downtime_helper(d) for d in await downtimes_cursor.to_list(length=None)]
        coversheet_dict["spareTruckInfos"] = [sparetruckinfo_helper(d) for d in await spares_cursor.to_list(length=None)]
        
        return coversheet_dict
    except Exception as e:
        print(f"Error en expansión de datos: {e}")
        raise


# ===========================
# RUTAS
# ===========================

@router.get("/")
async def get_all_coversheets(
    page: int = 1,
    limit: int = 50,
    start_date: str = None,
    end_date: str = None,
    truck_id: str = None,
    driver_id: str = None,
    route_id: str = None,
    sort_by: str = "date",
    sort_order: int = -1
):
    """
    Obtiene coversheets con paginación y filtros.
    
    Parámetros:
    - page: Número de página (default: 1)
    - limit: Registros por página (default: 50, max: 500)
    - start_date: Fecha inicio (formato: YYYY-MM-DD)
    - end_date: Fecha fin (formato: YYYY-MM-DD)
    - truck_id: Filtrar por camión
    - driver_id: Filtrar por conductor
    - route_id: Filtrar por ruta
    - sort_by: Campo para ordenar (default: "date")
    - sort_order: Orden (1: ascendente, -1: descendente)
    
    Ejemplos:
    - GET /api/coversheets/ → Primera página (50 registros)
    - GET /api/coversheets/?page=2&limit=100 → Segunda página (100 registros)
    - GET /api/coversheets/?start_date=2025-01-01&end_date=2025-12-31
    - GET /api/coversheets/?driver_id=ABC123&truck_id=XYZ789
    """
    try:
        # Validar parámetros
        if page < 1:
            return error_response("El parámetro 'page' debe ser >= 1", status_code=400)
        if limit < 1 or limit > 500:
            return error_response("El parámetro 'limit' debe estar entre 1 y 500", status_code=400)
        
        # Construir query de filtros
        query = {"active": True}  # ✅ Solo mostrar coversheets activos (soft delete)
        tz = ZoneInfo("America/Denver")
        
        # Filtro de fechas
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    start = start.replace(tzinfo=tz)
                    date_filter["$gte"] = start
                except ValueError:
                    return error_response("Formato de start_date inválido. Usa YYYY-MM-DD", status_code=400)
            
            if end_date:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    end = end.replace(tzinfo=tz) + timedelta(days=1)
                    date_filter["$lt"] = end
                except ValueError:
                    return error_response("Formato de end_date inválido. Usa YYYY-MM-DD", status_code=400)
            
            if date_filter:
                query["date"] = date_filter
        
        # Filtros por IDs (convertir strings a ObjectId)
        if truck_id:
            if ObjectId.is_valid(truck_id):
                query["truck_id"] = ObjectId(truck_id)
            else:
                return error_response("truck_id inválido", status_code=400)
                
        if driver_id:
            if ObjectId.is_valid(driver_id):
                query["driver_id"] = ObjectId(driver_id)
            else:
                return error_response("driver_id inválido", status_code=400)
        
        if route_id:
            if ObjectId.is_valid(route_id):
                query["route_id"] = ObjectId(route_id)
            else:
                return error_response("route_id inválido", status_code=400)
        
        # Calcular skip para paginación
        skip = (page - 1) * limit
        
        # Contar total de documentos que coinciden con los filtros
        total_count = await coversheets_collection.count_documents(query)
        
        # Obtener documentos con paginación
        cursor = coversheets_collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        
        # Procesar documentos
        coversheets = [coversheet_helper(d) for d in docs]
        
        # Calcular metadata de paginación
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        return success_response({
            "data": coversheets,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "filters": {
                "start_date": start_date,
                "end_date": end_date,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "route_id": route_id,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        })
    except Exception as e:
        return error_response(f"Error al obtener coversheets: {str(e)}")


@router.get("/by-date/{date_str}")
async def get_coversheets_by_date(date_str: str):
    """
    Obtiene coversheets de una fecha específica.
    
    Ejemplo: GET /api/coversheets/by-date/2025-01-30
    """
    try:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return error_response("Formato inválido. Usa YYYY-MM-DD", status_code=400)

        tz = ZoneInfo("America/Denver")
        start = datetime(query_date.year, query_date.month, query_date.day, tzinfo=tz)
        end = start + timedelta(days=1)

        # ✅ Filtrar solo coversheets activos
        cursor = coversheets_collection.find({
            "date": {"$gte": start, "$lt": end},
            "active": True
        })
        docs = await cursor.to_list(length=None)
        return success_response([coversheet_helper(d) for d in docs])
    except Exception as e:
        return error_response(f"Error al obtener coversheets por fecha: {str(e)}")


@router.get("/{id}")
async def get_coversheet_by_id(id: str, expand: bool = False):
    """
    Obtiene un coversheet por ID.
    
    Parámetros:
    - id: ID del coversheet
    - expand: Si es True, incluye loads, downtimes y spareTruckInfos
    
    Ejemplos:
    - GET /api/coversheets/685594bedb4f505f5f680e2d9
    - GET /api/coversheets/685594bedb4f505f5f680e2d9?expand=true
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
            
        # ✅ Filtrar solo coversheets activos
        doc = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not doc:
            return error_response("Coversheet no encontrada o está eliminada", status_code=404)
        
        # Si expand=true, incluir relaciones
        if expand:
            data = await expand_related_data_from_doc(doc)
            return success_response(data)
        else:
            return success_response(coversheet_helper(doc))
        
    except Exception as e:
        return error_response(f"Error al obtener coversheet: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coversheet(coversheet: CoverSheetModel):
    """
    Crea un nuevo coversheet.
    
    La fecha se convierte automáticamente a medianoche en la zona horaria de Denver.
    Se realiza desnormalización de nombres para optimizar queries.
    """
    try:
        data = coversheet.model_dump()
        
        # ✅ PASO 1: Convertir IDs a ObjectId Y desnormalizar nombres
        # Truck
        if data.get("truck_id"):
            data["truck_id"] = ObjectId(data["truck_id"])
            truck_doc = await trucks_collection.find_one({"_id": data["truck_id"]})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]
        
        # Route
        if data.get("route_id"):
            data["route_id"] = ObjectId(data["route_id"])
            route_doc = await routes_collection.find_one({"_id": data["route_id"]})
            if route_doc and route_doc.get("routeNumber"):
                data["routeNumber"] = route_doc["routeNumber"]
        
        # Driver
        if data.get("driver_id"):
            data["driver_id"] = ObjectId(data["driver_id"])
            driver_doc = await drivers_collection.find_one({"_id": data["driver_id"]})
            if driver_doc and driver_doc.get("name"):
                data["driverName"] = driver_doc["name"]
        
        # ✅ PASO 2: Establecer fechas con timezone correcto
        tz = ZoneInfo("America/Denver")
        now_denver = datetime.now(tz)
        
        # Si el frontend envió una fecha, usarla; si no, usar la fecha actual
        if data.get("date"):
            frontend_date = data["date"]
            
            # Convertir a Denver timezone
            if frontend_date.tzinfo is None:
                frontend_date_denver = frontend_date.replace(tzinfo=tz)
            else:
                frontend_date_denver = frontend_date.astimezone(tz)
            
            # Establecer a medianoche en Denver
            data["date"] = datetime(
                frontend_date_denver.year,
                frontend_date_denver.month,
                frontend_date_denver.day,
                0, 0, 0, 0,
                tzinfo=tz
            )
        else:
            # Usar fecha actual a medianoche
            data["date"] = datetime(
                now_denver.year,
                now_denver.month,
                now_denver.day,
                0, 0, 0, 0,
                tzinfo=tz
            )
        
        data["createdAt"] = now_denver
        data["updatedAt"] = None
        
        # ✅ PASO 3: Establecer active en True
        data["active"] = data.get("active", True)
        
        # ✅ PASO 4: Insertar en la base de datos
        result = await coversheets_collection.insert_one(data)
        
        # ✅ PASO 5: Recuperar el documento insertado y devolverlo
        new_doc = await coversheets_collection.find_one({"_id": result.inserted_id})
        return success_response(coversheet_helper(new_doc), msg="Coversheet creada exitosamente")
        
    except Exception as e:
        return error_response(f"Error al crear coversheet: {str(e)}")


@router.put("/{id}")
async def update_coversheet(id: str, coversheet: CoverSheetModel):
    """
    Actualiza un coversheet existente.
    
    No permite actualizar el campo 'date' ni 'active' por seguridad.
    Actualiza automáticamente el campo 'updatedAt'.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)
        
        data = coversheet.model_dump(exclude_unset=True)
        
        # ✅ PASO 1: Prevenir actualización de campos sensibles
        if "date" in data:
            del data["date"]  # No permitir cambiar la fecha
        if "active" in data:
            del data["active"]  # No permitir cambiar active a través de este endpoint
        
        # ✅ PASO 2: Actualizar updatedAt
        tz = ZoneInfo("America/Denver")
        data["updatedAt"] = datetime.now(tz)
        
        # ✅ PASO 3: Convertir IDs a ObjectId y desnormalizar nombres si se actualizan
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
        
        # ✅ PASO 4: Actualizar solo si el coversheet está activo
        res = await coversheets_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )
        
        if res.matched_count == 0:
            return error_response(
                "Coversheet no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # ✅ PASO 5: Recuperar el documento actualizado y devolverlo
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
    Soft delete: Marca el coversheet y todos sus documentos relacionados como inactivos.
    
    Los documentos NO se eliminan físicamente, solo se marcan como active=False.
    Esto preserva el historial y permite recuperación si es necesario.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
        
        coversheet_oid = ObjectId(id)
        
        # Verificar si existe y está activo
        existing = await coversheets_collection.find_one({"_id": coversheet_oid})
        if not existing:
            return error_response("Coversheet no encontrada", status_code=404)
        
        if not existing.get("active", True):
            return error_response("La coversheet ya está eliminada", status_code=400)
        
        # ✅ SOFT DELETE: Marcar como inactivo
        tz = ZoneInfo("America/Denver")
        
        # Marcar coversheet como inactivo
        await coversheets_collection.update_one(
            {"_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(tz)
                }
            }
        )
        
        # Marcar todos los loads relacionados como inactivos
        await loads_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(tz)
                }
            }
        )
        
        # Marcar todos los downtimes relacionados como inactivos
        await downtimes_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(tz)
                }
            }
        )
        
        # Marcar todos los spare truck infos relacionados como inactivos
        await sparetruckinfos_collection.update_many(
            {"coversheet_ref_id": coversheet_oid},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(tz)
                }
            }
        )
        
        return success_response(
            {"id": id},
            msg="Coversheet y documentos relacionados eliminados (soft delete)"
        )
    except Exception as e:
        return error_response(f"Error al eliminar coversheet: {str(e)}")


@router.delete("/{id}/permanent")
async def permanent_delete_coversheet(id: str, current_user: str = Depends(get_current_user)):
    """
    ⚠️ HARD DELETE: Elimina permanentemente el coversheet y TODOS sus documentos relacionados.
    
    Esta operación es IRREVERSIBLE y eliminará físicamente:
    - El coversheet
    - Todos los loads asociados
    - Todos los downtimes asociados
    - Todos los spare truck infos asociados
    
    Usar con precaución. Para eliminación normal, usar DELETE /{id} (soft delete).
    Requiere autenticación de usuario.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de Coversheet inválido", status_code=400)
        
        coversheet_oid = ObjectId(id)
        
        # Verificar si existe (sin importar si está activo o no)
        existing = await coversheets_collection.find_one({"_id": coversheet_oid})
        if not existing:
            return error_response("Coversheet no encontrada", status_code=404)
        
        # ✅ HARD DELETE: Contar documentos relacionados antes de eliminar
        loads_count = await loads_collection.count_documents({"coversheet_ref_id": coversheet_oid})
        downtimes_count = await downtimes_collection.count_documents({"coversheet_ref_id": coversheet_oid})
        spares_count = await sparetruckinfos_collection.count_documents({"coversheet_ref_id": coversheet_oid})
        
        # Eliminar documentos relacionados
        await loads_collection.delete_many({"coversheet_ref_id": coversheet_oid})
        await downtimes_collection.delete_many({"coversheet_ref_id": coversheet_oid})
        await sparetruckinfos_collection.delete_many({"coversheet_ref_id": coversheet_oid})
        
        # Eliminar el coversheet
        result = await coversheets_collection.delete_one({"_id": coversheet_oid})
        
        if result.deleted_count == 1:
            total_deleted = loads_count + downtimes_count + spares_count
            return success_response(
                {
                    "id": id,
                    "deleted_related_documents": {
                        "loads": loads_count,
                        "downtimes": downtimes_count,
                        "spare_truck_infos": spares_count
                    }
                },
                msg=f"Coversheet y {total_deleted} documentos relacionados eliminados permanentemente"
            )
        else:
            return error_response("No se pudo eliminar la coversheet", status_code=500)
            
    except Exception as e:
        return error_response(f"Error al eliminar permanentemente: {str(e)}")


# ===========================
# RUTAS DE RELACIONES
# ===========================

@router.get("/{id}/load")
async def get_loads_of_coversheet(id: str):
    """Obtiene todos los loads de un coversheet específico."""
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)
        
        # Verificar que el coversheet existe y está activo
        coversheet = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=404)
        
        # Obtener loads activos
        cursor = loads_collection.find({
            "coversheet_ref_id": ObjectId(id),
            "active": True
        })
        loads = [load_helper(d) for d in await cursor.to_list(length=None)]
        
        return success_response(loads, msg="Loads obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener loads: {str(e)}")


@router.get("/{id}/downtime")
async def get_downtimes_of_coversheet(id: str):
    """Obtiene todos los downtimes de un coversheet específico."""
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)
        
        # Verificar que el coversheet existe y está activo
        coversheet = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=404)
        
        # Obtener downtimes activos
        cursor = downtimes_collection.find({
            "coversheet_ref_id": ObjectId(id),
            "active": True
        })
        downtimes = [downtime_helper(d) for d in await cursor.to_list(length=None)]
        
        return success_response(downtimes, msg="Downtimes obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener downtimes: {str(e)}")


@router.get("/{id}/sparetruckinfo")
async def get_spares_of_coversheet(id: str):
    """Obtiene todos los spare truck infos de un coversheet específico."""
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)
        
        # Verificar que el coversheet existe y está activo
        coversheet = await coversheets_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not coversheet:
            return error_response("Coversheet no encontrado", status_code=404)
        
        # Obtener spare truck infos activos
        cursor = sparetruckinfos_collection.find({
            "coversheet_ref_id": ObjectId(id),
            "active": True
        })
        spares = [sparetruckinfo_helper(d) for d in await cursor.to_list(length=None)]
        
        return success_response(spares, msg="SpareTruckInfos obtenidos")
    except Exception as e:
        return error_response(f"Error al obtener spare truck infos: {str(e)}")