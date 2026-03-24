# Librerias
from fastapi import APIRouter, status, UploadFile, File, Form
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId
from typing import List, Optional

# Configuración de la base de datos y colecciones
from config.database import incidentDetails_collection

# Esquemas
from schemas.incidentdetail_scheme import incident_detail_helper

# ✅ OneDrive helper en lugar de disco local
from config.onedrive import smart_upload

# Rutas
router = APIRouter()

# Subcarpeta dentro de OneDrive para este módulo
ONEDRIVE_SUBFOLDER = "incidentdetails"


# ✅ Helper para convertir strings a bool (necesario para form-data)
def parse_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    return str(value).lower() in ("true", "1", "yes")


@router.post("/")
async def create_incident_detail(
    incidentDescription: Optional[str] = Form(None),
    actionEventCondition: Optional[str] = Form(None),
    wereAnyVehiclesTowed: Optional[str] = Form(None),   # ✅ str en lugar de bool
    wasAnyOneHurt: Optional[str] = Form(None),           # ✅ str en lugar de bool
    describeAnyInjuries: Optional[str] = Form(None),
    damageToAceTruck: Optional[str] = Form(None),
    whatDamageWasDone: Optional[str] = Form(None),
    incidentInThePastYear: Optional[str] = Form(None),  # ✅ str en lugar de bool
    listDatesOfIncidents: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
    generalInformation_ref_id: str = Form(...),
):
    try:
        # ✅ Convertir strings a bool
        wereAnyVehiclesTowed_bool = parse_bool(wereAnyVehiclesTowed)
        wasAnyOneHurt_bool = parse_bool(wasAnyOneHurt)
        incidentInThePastYear_bool = parse_bool(incidentInThePastYear)
        image_urls = []

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

                if len(contents) > 10 * 1024 * 1024:
                    return error_response(
                        f"The file '{image.filename}' exceeds the maximum size of 10MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                # ✅ Subir a OneDrive — retorna la webUrl del archivo
                file_url = await smart_upload(contents, image.filename, ONEDRIVE_SUBFOLDER)
                image_urls.append(file_url)

        data = {
            "incidentDescription": incidentDescription,
            "actionEventCondition": actionEventCondition,
            "wereAnyVehiclesTowed": wereAnyVehiclesTowed_bool,
            "wasAnyOneHurt": wasAnyOneHurt_bool,
            "describeAnyInjuries": describeAnyInjuries,
            "damageToAceTruck": damageToAceTruck,
            "whatDamageWasDone": whatDamageWasDone,
            "incidentInThePastYear": incidentInThePastYear_bool,
            "listDatesOfIncidents": listDatesOfIncidents,
            "images": image_urls,
            # "image_path": image_urls[0] if image_urls else None,  # primera imagen como preview
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
    wereAnyVehiclesTowed: Optional[str] = Form(None),   # ✅ str en lugar de bool
    wasAnyOneHurt: Optional[str] = Form(None),           # ✅ str en lugar de bool
    describeAnyInjuries: Optional[str] = Form(None),
    damageToAceTruck: Optional[str] = Form(None),
    whatDamageWasDone: Optional[str] = Form(None),
    incidentInThePastYear: Optional[str] = Form(None),  # ✅ str en lugar de bool
    listDatesOfIncidents: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=None),
):
    try:
        # ✅ Convertir strings a bool
        wereAnyVehiclesTowed_bool = parse_bool(wereAnyVehiclesTowed)
        wasAnyOneHurt_bool = parse_bool(wasAnyOneHurt)
        incidentInThePastYear_bool = parse_bool(incidentInThePastYear)

        existing = await incidentDetails_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if not existing:
            return error_response("Incident detail no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        # Mantener URLs existentes y agregar las nuevas
        image_urls = existing.get("images", [])

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

                if len(contents) > 10 * 1024 * 1024:
                    return error_response(
                        f"The image '{image.filename}' exceeds the maximum allowed size of 10MB.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                # ✅ Subir a OneDrive
                file_url = await smart_upload(contents, image.filename, ONEDRIVE_SUBFOLDER)
                image_urls.append(file_url)

        data = {
            "incidentDescription": incidentDescription,
            "actionEventCondition": actionEventCondition,
            "wereAnyVehiclesTowed": wereAnyVehiclesTowed_bool,
            "wasAnyOneHurt": wasAnyOneHurt_bool,
            "describeAnyInjuries": describeAnyInjuries,
            "damageToAceTruck": damageToAceTruck,
            "whatDamageWasDone": whatDamageWasDone,
            "incidentInThePastYear": incidentInThePastYear_bool,
            "listDatesOfIncidents": listDatesOfIncidents,
            "images": image_urls,
            # "image_path": image_urls[0] if image_urls else existing.get("image_path"),
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