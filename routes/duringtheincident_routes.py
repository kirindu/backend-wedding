# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelo
from models.duringtheincident_model import DuringTheIncidentModel

# Configuración de la base de datos y colecciones
from config.database import (
    duringTheIncidents_collection,
    safetyPersonsNotified_collection,
    whoDidYouSendThePicturesTo_collection,
    directions_collection,
    weatherConditions_collection,
    roadConditions_collection,
)

# Esquema
from schemas.duringtheincident_scheme import during_the_incident_helper

# Rutas
router = APIRouter()

# Mapeo de lookups: campo_id → (colección, campo_fuente, campo_destino_denormalizado)
LOOKUP_MAPS = {
    "safetyPersonNotified_id":       (safetyPersonsNotified_collection,      "safetyPersonNotifiedName",     "safetyPersonNotifiedName"),
    "whoDidYouSendThePicturesTo_id": (whoDidYouSendThePicturesTo_collection,  "whoDidYouSendThePictureToName", "whoDidYouSendThePictureToName"),
    "directionYouWereTraveling_id":  (directions_collection,                  "directionName",                "directionName"),
    "weatherCondition_id":           (weatherConditions_collection,            "weatherName",                  "weatherName"),
    "roadCondition_id":              (roadConditions_collection,               "roadConditionName",            "roadConditionName"),
}


async def resolve_lookup_fields(data: dict) -> dict:
    """Convierte IDs string a ObjectId y resuelve nombres denormalizados."""
    for field, (col, source_key, target_key) in LOOKUP_MAPS.items():
        if data.get(field):
            data[field] = ObjectId(data[field])
            doc = await col.find_one({"_id": data[field]})
            data[target_key] = doc.get(source_key) if doc else None
        else:
            data[field] = None
            data[target_key] = None
    return data


@router.post("/")
async def create_during_the_incident(during_the_incident: DuringTheIncidentModel):
    try:
        data = during_the_incident.model_dump()

        # Convertir generalInformation_ref_id a ObjectId
        if data.get("generalInformation_ref_id"):
            data["generalInformation_ref_id"] = ObjectId(data["generalInformation_ref_id"])

        # Resolver lookups y denormalizar nombres
        data = await resolve_lookup_fields(data)

        # Audit fields
        tz = ZoneInfo("America/Denver")
        data["createdAt"] = datetime.now(tz)
        data["updatedAt"] = None
        data["active"] = True

        new = await duringTheIncidents_collection.insert_one(data)
        created = await duringTheIncidents_collection.find_one({"_id": new.inserted_id})

        return success_response(
            during_the_incident_helper(created),
            msg="During The Incident creado exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear During The Incident: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_during_the_incidents():
    try:
        items = [
            during_the_incident_helper(d)
            async for d in duringTheIncidents_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(items, msg="Lista de During The Incidents obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener During The Incidents: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_during_the_incident(id: str):
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)

        item = await duringTheIncidents_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if item:
            return success_response(
                during_the_incident_helper(item),
                msg="During The Incident encontrado"
            )
        return error_response(
            "During The Incident no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener During The Incident: {str(e)}")


@router.put("/{id}")
async def update_during_the_incident(id: str, during_the_incident: DuringTheIncidentModel):
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)

        data = during_the_incident.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # Resolver lookups y denormalizar nombres
        data = await resolve_lookup_fields(data)

        # Audit field
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await duringTheIncidents_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "During The Incident no encontrado o no está activo",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await duringTheIncidents_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            during_the_incident_helper(updated),
            msg="During The Incident actualizado"
        )
    except Exception as e:
        return error_response(f"Error al actualizar During The Incident: {str(e)}")


@router.delete("/{id}")
async def delete_during_the_incident(id: str):
    """Soft delete — marca como inactivo en lugar de eliminar."""
    try:
        if not ObjectId.is_valid(id):
            return error_response("ID inválido", status_code=400)

        item = await duringTheIncidents_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not item:
            return error_response(
                "During The Incident no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await duringTheIncidents_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="During The Incident eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar During The Incident: {str(e)}")


@router.get("/by-general-informacion/{generalInformation_id}")
async def get_during_the_incidents_by_general_information(generalInformation_id: str):
    try:
        if not ObjectId.is_valid(generalInformation_id):
            return error_response("ID inválido", status_code=400)

        gi_oid = ObjectId(generalInformation_id)

        items = [
            during_the_incident_helper(d)
            async for d in duringTheIncidents_collection.find({
                "generalInformation_ref_id": gi_oid,
                "active": True
            })
        ]

        return success_response(
            items,
            msg=f"During The Incidents de la general_information {generalInformation_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener During The Incidents por general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )