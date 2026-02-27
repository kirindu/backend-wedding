# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelos
from models.duringtheincident_model import DuringTheIncidentModel

# Configuración de la base de datos y colecciones
from config.database import (
    duringTheIncidents_collection,
    directions_collection,
    weatherConditions_collection,   
    roadConditions_collection,
    safetyPersons_collection,
    whoDidYouSendThePicturesTo_collection       
)

# Esquemas
from schemas.duringtheincident_scheme import during_the_incident_helper

# Rutas
router = APIRouter()


async def resolve_lookup_fields(data: dict):
    """
    ✅ Helper para convertir IDs a ObjectId y resolver los nombres denormalizados.
    Separado para no repetir lógica entre POST y PUT.
    """
    # Convertir safetyPersonNotified_id
    if data.get("safetyPersonNotified_id"):
        data["safetyPersonNotified_id"] = ObjectId(data["safetyPersonNotified_id"])
        safety_person_doc = await safetyPersons_collection.find_one({"_id": data["safetyPersonNotified_id"]})
        data["safetyPersonNotifiedName"] = safety_person_doc.get("safetyPersonNotifiedName") if safety_person_doc else None     
    
    # Convertir whoDidYouSendThePictureTo_id
    if data.get("whoDidYouSendThePictureTo_id"):
        data["whoDidYouSendThePictureTo_id"] = ObjectId(data["whoDidYouSendThePictureTo_id"])
        who_doc = await whoDidYouSendThePicturesTo_collection.find_one({"_id": data["whoDidYouSendThePictureTo_id"]})
        data["whoDidYouSendThePictureToName"] = who_doc.get("whoDidYouSendThePictureToName") if who_doc else None       
                
    
    # Convertir directionYouWereTraveling_id
    if data.get("directionYouWereTraveling_id"):
        data["directionYouWereTraveling_id"] = ObjectId(data["directionYouWereTraveling_id"])
        direction_doc = await directions_collection.find_one({"_id": data["directionYouWereTraveling_id"]})
        data["directionName"] = direction_doc.get("directionName") if direction_doc else None

    # Convertir weatherConditions_id
    if data.get("weatherConditions_id"):
        data["weatherConditions_id"] = ObjectId(data["weatherConditions_id"])
        weather_doc = await weatherConditions_collection.find_one({"_id": data["weatherConditions_id"]})
        data["weatherName"] = weather_doc.get("weatherName") if weather_doc else None

    # Convertir roadConditions_id
    if data.get("roadConditions_id"):
        data["roadConditions_id"] = ObjectId(data["roadConditions_id"])
        road_doc = await roadConditions_collection.find_one({"_id": data["roadConditions_id"]})
        data["roadConditionName"] = road_doc.get("roadConditionName") if road_doc else None

    return data


@router.post("/")
async def create_during_the_incident(during_the_incident: DuringTheIncidentModel):
    try:
        data = during_the_incident.model_dump()

        # Convertir generalInformation_ref_id a ObjectId
        if data.get("generalInformation_ref_id"):
            data["generalInformation_ref_id"] = ObjectId(data["generalInformation_ref_id"])

        # ✅ Resolver lookups de forma limpia
        data = await resolve_lookup_fields(data)

        # ✅ Audit fields
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        new = await duringTheIncidents_collection.insert_one(data)
        created = await duringTheIncidents_collection.find_one({"_id": new.inserted_id})

        return success_response(
            during_the_incident_helper(created),
            msg="During the incident creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear during the incident: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_during_the_incidents():
    try:
        during_the_incidents = [
            during_the_incident_helper(d)
            async for d in duringTheIncidents_collection.find({"active": True})
        ]
        return success_response(during_the_incidents, msg="Lista de during the incidents obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener during the incidents: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_during_the_incident(id: str):
    try:
        during_the_incident = await duringTheIncidents_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if during_the_incident:
            return success_response(during_the_incident_helper(during_the_incident), msg="During the incident encontrada")
        return error_response(
            "During the incident no encontrada",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener during the incident: {str(e)}")


@router.put("/{id}")
async def update_during_the_incident(id: str, during_the_incident: DuringTheIncidentModel):
    try:
        data = during_the_incident.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # ✅ Resolver lookups de forma limpia
        data = await resolve_lookup_fields(data)

        # ✅ Audit field
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await duringTheIncidents_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "During the incident no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await duringTheIncidents_collection.find_one({"_id": ObjectId(id)})
        return success_response(during_the_incident_helper(updated), msg="During the incident actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar during the incident: {str(e)}")


@router.delete("/{id}")
async def delete_during_the_incident(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        during_the_incident = await duringTheIncidents_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not during_the_incident:
            return error_response(
                "During the incident no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await duringTheIncidents_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="During the incident eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar during the incident: {str(e)}")


@router.get("/by-general-informacion/{generalInformation_id}")
async def get_during_the_incidents_by_general_information(generalInformation_id: str):
    try:
        generalInformation_oid = ObjectId(generalInformation_id)

        during_the_incidents = [
            during_the_incident_helper(d)
            async for d in duringTheIncidents_collection.find({
                "generalInformation_ref_id": generalInformation_oid,
                "active": True
            })
        ]

        return success_response(
            during_the_incidents,
            msg=f"During the incidents de la general_information {generalInformation_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener during the incidents por general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )