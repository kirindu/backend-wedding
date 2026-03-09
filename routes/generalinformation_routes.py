# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelos
from models.generalinformation_model import GeneralInformationModel

# Configuración de la base de datos y colecciones
from config.database import (
    generalinformations_collection,
    employees_collection,
    trucks_collection,
    depts_collection,
    supervisors_collection,
    typeOfIncidents_collection,
    duringTheIncidents_collection,
    supervisorNotes_collection,
    incidentDetails_collection,
)

# Esquemas - Sección principal
from schemas.generalinformation_scheme import general_information_helper

# Esquemas - Secciones hijas
from schemas.duringtheincident_scheme import during_the_incident_helper
from schemas.supervisornote_scheme import supervisor_note_helper
from schemas.incidentdetail_scheme import incident_detail_helper

# Rutas
router = APIRouter()

# Mapeo de lookups: campo_id → (colección, campo_fuente, campo_destino_denormalizado)
LOOKUP_MAPS = {
    "employee_id":       (employees_collection,      "employeeName",       "employeeName"),
    "truck_id":          (trucks_collection,          "truckNumber",        "truckNumber"),
    "dept_id":           (depts_collection,           "deptName",           "deptName"),
    "supervisor_id":     (supervisors_collection,     "supervisorName",     "supervisorName"),
    "typeOfIncident_id": (typeOfIncidents_collection, "typeOfIncidentName", "typeOfIncidentName"),
}


# --- FUNCIONES INTERNAS (HELPERS) ---

async def resolve_lookup_fields(data: dict) -> dict:
    """
    Convierte IDs string a ObjectId y resuelve los nombres denormalizados
    para mostrar en el frontend sin necesidad de joins adicionales.
    """
    for field, (col, source_key, target_key) in LOOKUP_MAPS.items():
        if data.get(field):
            data[field] = ObjectId(data[field])
            doc = await col.find_one({"_id": data[field]})
            data[target_key] = doc.get(source_key) if doc else None
    return data


async def expand_related_data_from_doc(doc: dict) -> dict:
    """
    Expande las secciones hijas (duringTheIncident, supervisorNote, incidentDetail)
    directamente desde el documento MongoDB original (con ObjectIds).
    """
    try:
        gi_id = doc["_id"]  # Ya es ObjectId

        during_cursor  = duringTheIncidents_collection.find({"generalInformation_ref_id": gi_id, "active": True})
        notes_cursor   = supervisorNotes_collection.find({"generalInformation_ref_id": gi_id, "active": True})
        details_cursor = incidentDetails_collection.find({"generalInformation_ref_id": gi_id, "active": True})

        gi_dict = general_information_helper(doc)

        gi_dict["duringTheIncidents"] = [during_the_incident_helper(d) for d in await during_cursor.to_list(length=None)]
        gi_dict["supervisorNotes"]    = [supervisor_note_helper(d)      for d in await notes_cursor.to_list(length=None)]
        gi_dict["incidentDetails"]    = [incident_detail_helper(d)      for d in await details_cursor.to_list(length=None)]

        return gi_dict
    except Exception as e:
        print(f"Error en expansión de datos: {e}")
        raise


def _normalize_date_to_denver(date_value, tz) -> datetime:
    """
    Normaliza cualquier fecha a medianoche en zona horaria Denver.
    Si viene en UTC desde el frontend, la convierte correctamente antes
    de extraer año/mes/día para evitar desfases de día.
    """
    if date_value.tzinfo is None:
        date_denver = date_value.replace(tzinfo=tz)
    else:
        date_denver = date_value.astimezone(tz)

    return datetime(
        date_denver.year,
        date_denver.month,
        date_denver.day,
        0, 0, 0, 0,
        tzinfo=tz
    )


# --- RUTAS ---

# 0. GET con paginación y filtros (debe ir ANTES que las rutas con path params)
@router.get("/")
async def get_all_general_informations(
    page: int = 1,
    limit: int = 50,
    start_date: str = None,
    end_date: str = None,
    employee_id: str = None,
    truck_id: str = None,
    dept_id: str = None,
    supervisor_id: str = None,
    typeOfIncident_id: str = None,
    sort_by: str = "date",
    sort_order: int = -1,
):
    """
    Obtiene general informations con paginación y filtros opcionales.

    Ejemplos:
    - GET /api/generalinformations/                                   → Primera página (50 registros)
    - GET /api/generalinformations/?page=2&limit=100                  → Segunda página
    - GET /api/generalinformations/?start_date=2025-01-01&end_date=2025-12-31
    - GET /api/generalinformations/?employee_id=ABC123&dept_id=XYZ
    """
    try:
        if page < 1:
            return error_response("El parámetro 'page' debe ser >= 1", status_code=400)
        if limit < 1 or limit > 500:
            return error_response("El parámetro 'limit' debe estar entre 1 y 500", status_code=400)

        query = {"active": True}
        tz = ZoneInfo("America/Denver")

        # --- Filtro de fechas sobre el campo date ---
        if start_date or end_date:
            date_filter = {}
            if start_date:
                try:
                    start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=tz)
                    date_filter["$gte"] = start
                except ValueError:
                    return error_response("Formato de start_date inválido. Usa YYYY-MM-DD", status_code=400)

            if end_date:
                try:
                    end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=tz) + timedelta(days=1)
                    date_filter["$lt"] = end
                except ValueError:
                    return error_response("Formato de end_date inválido. Usa YYYY-MM-DD", status_code=400)

            if date_filter:
                query["date"] = date_filter

        # --- Filtros por IDs relacionados ---
        id_filters = {
            "employee_id":       employee_id,
            "truck_id":          truck_id,
            "dept_id":           dept_id,
            "supervisor_id":     supervisor_id,
            "typeOfIncident_id": typeOfIncident_id,
        }

        for field, value in id_filters.items():
            if value:
                if not ObjectId.is_valid(value):
                    return error_response(f"{field} inválido", status_code=400)
                query[field] = ObjectId(value)

        # --- Paginación ---
        skip = (page - 1) * limit
        total_count = await generalinformations_collection.count_documents(query)

        cursor = generalinformations_collection.find(query).sort(sort_by, sort_order).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)

        general_informations = [general_information_helper(d) for d in docs]
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0

        return success_response({
            "data": general_informations,
            "pagination": {
                "page": page,
                "limit": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
            "filters": {
                "start_date":        start_date,
                "end_date":          end_date,
                "employee_id":       employee_id,
                "truck_id":          truck_id,
                "dept_id":           dept_id,
                "supervisor_id":     supervisor_id,
                "typeOfIncident_id": typeOfIncident_id,
                "sort_by":           sort_by,
                "sort_order":        sort_order,
            }
        }, msg="Lista de general informations obtenida")

    except Exception as e:
        return error_response(f"Error al obtener general informations: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 1. RUTA DE FECHA (debe ir ANTES de /{id} para evitar conflictos de routing)
@router.get("/by-date/{date_str}")
async def get_general_informations_by_date(date_str: str):
    """
    Filtra general informations por fecha de incidente.
    Ejemplo: GET /api/generalinformations/by-date/2025-06-15
    """
    try:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return error_response("Formato inválido. Usa YYYY-MM-DD", status_code=400)

        tz = ZoneInfo("America/Denver")
        start = datetime(query_date.year, query_date.month, query_date.day, tzinfo=tz)
        end = start + timedelta(days=1)

        cursor = generalinformations_collection.find({
            "date": {"$gte": start, "$lt": end},
            "active": True
        })
        docs = await cursor.to_list(length=None)
        return success_response([general_information_helper(d) for d in docs])
    except Exception as e:
        return error_response(str(e))


# 2. RUTA DE ID ÚNICO — retorna la general information expandida con sus secciones hijas
@router.get("/{id}")
async def get_general_information(id: str):
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de General Information inválido", status_code=400)

        doc = await generalinformations_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not doc:
            return error_response("General information no encontrada o está eliminada", status_code=status.HTTP_404_NOT_FOUND)

        # Retorna el documento expandido con duringTheIncidents, supervisorNotes e incidentDetails
        data = await expand_related_data_from_doc(doc)
        return success_response(data, msg="General information encontrada")
    except Exception as e:
        return error_response(f"Error al obtener general information: {str(e)}")


# 3. POST
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_general_information(general_information: GeneralInformationModel):
    try:
        data = general_information.model_dump()

        # PASO 1: Desnormalizar lookups (convierte IDs y guarda nombres en el documento)
        data = await resolve_lookup_fields(data)

        # PASO 2: Normalizar date a medianoche en Denver
        tz = ZoneInfo("America/Denver")
        now_denver = datetime.now(tz)

        if data.get("date"):
            data["date"] = _normalize_date_to_denver(data["date"], tz)
        else:
            data["date"] = datetime(now_denver.year, now_denver.month, now_denver.day, 0, 0, 0, 0, tzinfo=tz)

        # PASO 3: Audit fields
        data["createdAt"] = now_denver
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        # PASO 4: Insertar
        result = await generalinformations_collection.insert_one(data)
        new_doc = await generalinformations_collection.find_one({"_id": result.inserted_id})

        return success_response(
            general_information_helper(new_doc),
            msg="General information creada exitosamente"
        )
    except Exception as e:
        return error_response(f"Error al crear general information: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 4. PUT
@router.put("/{id}")
async def update_general_information(id: str, general_information: GeneralInformationModel):
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)

        data = general_information.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # PASO 1: Desnormalizar lookups
        data = await resolve_lookup_fields(data)

        # PASO 2: Normalizar date si se envió
        tz = ZoneInfo("America/Denver")
        if "date" in data and data["date"] is not None:
            data["date"] = _normalize_date_to_denver(data["date"], tz)

        # PASO 3: Audit field
        data["updatedAt"] = datetime.now(tz)

        res = await generalinformations_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "General information no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await generalinformations_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            general_information_helper(updated),
            msg="General information actualizada"
        )
    except Exception as e:
        return error_response(f"Error al actualizar general information: {str(e)}")


# 5. RUTAS HIJAS (referencia inversa — deben ir ANTES del DELETE para evitar conflictos)
@router.get("/{id}/duringtheincident")
async def get_during_the_incidents_of_general_information(id: str):
    """Retorna todas las secciones 'During The Incident' de una General Information."""
    if not ObjectId.is_valid(id):
        return error_response("ID inválido", status_code=400)
    cursor = duringTheIncidents_collection.find({"generalInformation_ref_id": ObjectId(id), "active": True})
    return success_response([during_the_incident_helper(d) for d in await cursor.to_list(length=None)])


@router.get("/{id}/supervisornote")
async def get_supervisor_notes_of_general_information(id: str):
    """Retorna todas las Supervisor Notes de una General Information."""
    if not ObjectId.is_valid(id):
        return error_response("ID inválido", status_code=400)
    cursor = supervisorNotes_collection.find({"generalInformation_ref_id": ObjectId(id), "active": True})
    return success_response([supervisor_note_helper(d) for d in await cursor.to_list(length=None)])


@router.get("/{id}/incidentdetail")
async def get_incident_details_of_general_information(id: str):
    """Retorna todos los Incident Details de una General Information."""
    if not ObjectId.is_valid(id):
        return error_response("ID inválido", status_code=400)
    cursor = incidentDetails_collection.find({"generalInformation_ref_id": ObjectId(id), "active": True})
    return success_response([incident_detail_helper(d) for d in await cursor.to_list(length=None)])


# 6. SOFT DELETE
@router.delete("/{id}")
async def delete_general_information(id: str):
    """
    Soft delete — marca la General Information como inactiva (active: False).
    Los documentos hijos relacionados NO se eliminan.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de General Information inválido", status_code=400)

        gi_id = ObjectId(id)
        existing = await generalinformations_collection.find_one({"_id": gi_id})

        if not existing:
            return error_response("General information no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        if not existing.get("active", True):
            return error_response("La general information ya está eliminada", status_code=400)

        tz = ZoneInfo("America/Denver")
        result = await generalinformations_collection.update_one(
            {"_id": gi_id},
            {"$set": {"active": False, "updatedAt": datetime.now(tz)}}
        )

        if result.modified_count == 1:
            return success_response({"id": id}, msg="General information eliminada exitosamente (soft delete)")
        else:
            return error_response("No se pudo eliminar la general information", status_code=500)

    except Exception as e:
        return error_response(f"Error al eliminar general information: {str(e)}")


# 7. HARD DELETE (cascada completa)
@router.delete("/{id}/permanent")
async def permanent_delete_general_information(id: str):
    """
    ⚠️ HARD DELETE — Elimina permanentemente la General Information y TODOS
    sus documentos relacionados (duringTheIncidents, supervisorNotes, incidentDetails).

    Esta operación es IRREVERSIBLE. Para eliminación normal usar DELETE /{id}.
    """
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID de General Information inválido", status_code=400)

        gi_id = ObjectId(id)

        existing = await generalinformations_collection.find_one({"_id": gi_id})
        if not existing:
            return error_response("General information no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        # Contar relacionados antes de eliminar (para el reporte de respuesta)
        during_count  = await duringTheIncidents_collection.count_documents({"generalInformation_ref_id": gi_id})
        notes_count   = await supervisorNotes_collection.count_documents({"generalInformation_ref_id": gi_id})
        details_count = await incidentDetails_collection.count_documents({"generalInformation_ref_id": gi_id})

        # Eliminar secciones hijas
        await duringTheIncidents_collection.delete_many({"generalInformation_ref_id": gi_id})
        await supervisorNotes_collection.delete_many({"generalInformation_ref_id": gi_id})
        await incidentDetails_collection.delete_many({"generalInformation_ref_id": gi_id})

        # Eliminar el documento principal
        result = await generalinformations_collection.delete_one({"_id": gi_id})

        if result.deleted_count == 1:
            total_related = during_count + notes_count + details_count
            return success_response(
                {
                    "id": id,
                    "deleted_related_documents": {
                        "duringTheIncidents": during_count,
                        "supervisorNotes":    notes_count,
                        "incidentDetails":    details_count,
                    }
                },
                msg=f"General information y {total_related} documentos relacionados eliminados permanentemente"
            )
        else:
            return error_response("No se pudo eliminar la general information", status_code=500)

    except Exception as e:
        return error_response(f"Error al eliminar permanentemente: {str(e)}")