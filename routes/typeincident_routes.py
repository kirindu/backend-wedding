from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.typeincident_model import TypeIncidentModel

# Configuración de la base de datos y colecciones
from config.database import typeOfIncidents_collection

# Esquemas
from schemas.typeincident_scheme import type_incident_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_type_incident(type_incident: TypeIncidentModel):
    try:
        data = type_incident.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await typeOfIncidents_collection.insert_one(data)
        created = await typeOfIncidents_collection.find_one({"_id": new.inserted_id})
        return success_response(type_incident_helper(created), msg="Type of incident creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear type of incident: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_type_incidents():
    try:
        type_incidents = [
            type_incident_helper(t)
            async for t in typeOfIncidents_collection.find({"active": True}).sort("typeIncidentName", 1)
        ]
        return success_response(type_incidents, msg="Lista de type of incidents obtenida")
    except Exception as e:
        return error_response(f"Error al obtener type of incidents: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_type_incident(id: str):
    try:
        type_incident = await typeOfIncidents_collection.find_one({"_id": ObjectId(id)})
        if type_incident:
            return success_response(type_incident_helper(type_incident), msg="Type of incident encontrado")
        return error_response("Type of incident no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener type of incident: {str(e)}")


@router.put("/{id}")
async def update_type_incident(id: str, type_incident: TypeIncidentModel):
    try:
        update_data = type_incident.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await typeOfIncidents_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Type of incident no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await typeOfIncidents_collection.find_one({"_id": ObjectId(id)})
        return success_response(type_incident_helper(updated), msg="Type of incident actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar type of incident: {str(e)}")


@router.delete("/{id}")
async def delete_type_incident(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        type_incident = await typeOfIncidents_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not type_incident:
            return error_response(
                "Type of incident no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await typeOfIncidents_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Type of incident eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar type of incident: {str(e)}")