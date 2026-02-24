# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
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
)

# Esquemas
from schemas.generalinformation_scheme import general_information_helper

# Rutas
router = APIRouter()


async def resolve_lookup_fields(data: dict):
    """
    Convierte IDs a ObjectId y resuelve los nombres denormalizados
    para mostrar en el frontend sin necesidad de joins adicionales.
    """
    # Employee
    if data.get("employee_id"):
        data["employee_id"] = ObjectId(data["employee_id"])
        doc = await employees_collection.find_one({"_id": data["employee_id"]})
        data["employeeName"] = doc.get("employeeName") if doc else None

    # Truck
    if data.get("truck_id"):
        data["truck_id"] = ObjectId(data["truck_id"])
        doc = await trucks_collection.find_one({"_id": data["truck_id"]})
        data["truckNumber"] = doc.get("truckNumber") if doc else None  # ⚠️ Ajusta al nombre real del campo en truck_model

    # Dept
    if data.get("dept_id"):
        data["dept_id"] = ObjectId(data["dept_id"])
        doc = await depts_collection.find_one({"_id": data["dept_id"]})
        data["deptName"] = doc.get("deptName") if doc else None

    # Supervisor
    if data.get("supervisor_id"):
        data["supervisor_id"] = ObjectId(data["supervisor_id"])
        doc = await supervisors_collection.find_one({"_id": data["supervisor_id"]})
        data["supervisorName"] = doc.get("supervisorName") if doc else None  # ⚠️ Ajusta al nombre real del campo en supervisor_model

    # Type of Incident
    if data.get("typeOfIncident_id"):
        data["typeOfIncident_id"] = ObjectId(data["typeOfIncident_id"])
        doc = await typeOfIncidents_collection.find_one({"_id": data["typeOfIncident_id"]})
        data["typeOfIncidentName"] = doc.get("typeOfIncidentName") if doc else None  # ⚠️ Ajusta al nombre real del campo en typeincident_model

    return data


@router.post("/")
async def create_general_information(general_information: GeneralInformationModel):
    try:
        data = general_information.model_dump()

        # Resolver lookups
        data = await resolve_lookup_fields(data)

        # Audit fields
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        new = await generalinformations_collection.insert_one(data)
        created = await generalinformations_collection.find_one({"_id": new.inserted_id})

        return success_response(
            general_information_helper(created),
            msg="General information creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_general_informations():
    try:
        general_informations = [
            general_information_helper(g)
            async for g in generalinformations_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(general_informations, msg="Lista de general informations obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener general informations: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_general_information(id: str):
    try:
        general_information = await generalinformations_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if general_information:
            return success_response(
                general_information_helper(general_information),
                msg="General information encontrada"
            )
        return error_response(
            "General information no encontrada",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener general information: {str(e)}")


@router.put("/{id}")
async def update_general_information(id: str, general_information: GeneralInformationModel):
    try:
        data = general_information.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # Resolver lookups
        data = await resolve_lookup_fields(data)

        # Audit field
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

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


@router.delete("/{id}")
async def delete_general_information(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        general_information = await generalinformations_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not general_information:
            return error_response(
                "General information no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await generalinformations_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="General information eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar general information: {str(e)}")