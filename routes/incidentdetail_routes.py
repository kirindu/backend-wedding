# Librerias
from fastapi import APIRouter, status, UploadFile, File, Form
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId
from typing import List, Optional
import os
import uuid

# Configuración de la base de datos y colecciones
from config.database import incidentDetails_collection

# Esquemas
from schemas.incidentdetail_scheme import incident_detail_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_incident_detail(
    incidentDescription: Optional[str] = Form(None),
    actionEventCondition: Optional[str] = Form(None),
    wereAnyVehiclesTowed: Optional[bool] = Form(None),
    wasAnyOneHurt: Optional[bool] = Form(None),
    describeAnyInjuries: Optional[str] = Form(None),
    damageToAceTruck: Optional[str] = Form(None),
    whatDamageWasDone: Optional[str] = Form(None),
    incidentInThePastYear: Optional[bool] = Form(None),
    listDatesOfIncidents: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
    image_path: Optional[str] = Form(None),
    generalInformation_ref_id: str = Form(...),
):
    try:
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:
            for image in images:
                if not image or not image.filename:
                    continue

                if not image.content_type or not image.content_type.startswith("image/"):
                    return error_response(
                        f"The file '{image.filename}' is not an image.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    return error_response(
                        f"The file '{image.filename}' exceeds the maximum size of 5MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                image_paths.append(file_path)

        data = {
            "incidentDescription": incidentDescription,
            "actionEventCondition": actionEventCondition,
            "wereAnyVehiclesTowed": wereAnyVehiclesTowed,
            "wasAnyOneHurt": wasAnyOneHurt,
            "describeAnyInjuries": describeAnyInjuries,
            "damageToAceTruck": damageToAceTruck,
            "whatDamageWasDone": whatDamageWasDone,
            "incidentInThePastYear": incidentInThePastYear,
            "listDatesOfIncidents": listDatesOfIncidents,
            "images": image_paths if image_paths else [],
            "image_path": image_path,
            "generalInformation_ref_id": ObjectId(generalInformation_ref_id),
            "createdAt": datetime.now(ZoneInfo("America/Denver")),
            "updatedAt": None,
            "active": True,
        }

        new = await incidentDetails_collection.insert_one(data)
        created = await incidentDetails_collection.find_one({"_id": new.inserted_id})

        return success_response(
            incident_detail_helper(created),
            msg="Incident detail creado exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear incident detail: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_incident_details():
    try:
        incident_details = [
            incident_detail_helper(i)
            async for i in incidentDetails_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(incident_details, msg="Lista de incident details obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener incident details: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_incident_detail(id: str):
    try:
        incident_detail = await incidentDetails_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if incident_detail:
            return success_response(
                incident_detail_helper(incident_detail),
                msg="Incident detail encontrado"
            )
        return error_response(
            "Incident detail no encontrado",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener incident detail: {str(e)}")


@router.put("/{id}")
async def update_incident_detail(
    id: str,
    incidentDescription: Optional[str] = Form(None),
    actionEventCondition: Optional[str] = Form(None),
    wereAnyVehiclesTowed: Optional[bool] = Form(None),
    wasAnyOneHurt: Optional[bool] = Form(None),
    describeAnyInjuries: Optional[str] = Form(None),
    damageToAceTruck: Optional[str] = Form(None),
    whatDamageWasDone: Optional[str] = Form(None),
    incidentInThePastYear: Optional[bool] = Form(None),
    listDatesOfIncidents: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
    image_path: Optional[str] = Form(None),
):
    try:
        existing = await incidentDetails_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not existing:
            return error_response("Incident detail no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        # Mantener imágenes existentes y agregar las nuevas
        image_paths = existing.get("images", [])
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        if images:
            for image in images:
                if not image or not image.filename:
                    continue

                if not image.content_type or not image.content_type.startswith("image/"):
                    return error_response(
                        f"The file '{image.filename}' is not an image.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                contents = await image.read()
                if len(contents) > 5 * 1024 * 1024:
                    return error_response(
                        f"The image '{image.filename}' exceeds the maximum allowed size of 5MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                filename = f"{uuid.uuid4()}_{image.filename}"
                file_path = os.path.join(upload_dir, filename)
                with open(file_path, "wb") as buffer:
                    buffer.write(contents)
                image_paths.append(file_path)

        data = {
            "incidentDescription": incidentDescription,
            "actionEventCondition": actionEventCondition,
            "wereAnyVehiclesTowed": wereAnyVehiclesTowed,
            "wasAnyOneHurt": wasAnyOneHurt,
            "describeAnyInjuries": describeAnyInjuries,
            "damageToAceTruck": damageToAceTruck,
            "whatDamageWasDone": whatDamageWasDone,
            "incidentInThePastYear": incidentInThePastYear,
            "listDatesOfIncidents": listDatesOfIncidents,
            "images": image_paths,
            "image_path": image_path,
            "updatedAt": datetime.now(ZoneInfo("America/Denver")),
        }

        res = await incidentDetails_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "Incident detail no encontrado o no está activo",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await incidentDetails_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            incident_detail_helper(updated),
            msg="Incident detail actualizado"
        )
    except Exception as e:
        return error_response(f"Error al actualizar incident detail: {str(e)}")


@router.delete("/{id}")
async def delete_incident_detail(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        incident_detail = await incidentDetails_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not incident_detail:
            return error_response(
                "Incident detail no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await incidentDetails_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="Incident detail eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar incident detail: {str(e)}")


@router.get("/by-general-informacion/{generalInformation_id}")
async def get_incident_details_by_general_information(generalInformation_id: str):
    try:
        generalInformation_oid = ObjectId(generalInformation_id)

        incident_details = [
            incident_detail_helper(i)
            async for i in incidentDetails_collection.find({
                "generalInformation_ref_id": generalInformation_oid,
                "active": True
            })
        ]

        return success_response(
            incident_details,
            msg=f"Incident details de la general_information {generalInformation_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener incident details por general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )