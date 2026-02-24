# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelos
from models.supervisornote_model import SupervisorNoteModel

# Configuración de la base de datos y colecciones
from config.database import supervisorNotes_collection

# Esquemas
from schemas.supervisornote_scheme import supervisor_note_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_supervisor_note(supervisor_note: SupervisorNoteModel):
    try:
        data = supervisor_note.model_dump()

        # Convertir generalInformation_ref_id a ObjectId
        if data.get("generalInformation_ref_id"):
            data["generalInformation_ref_id"] = ObjectId(data["generalInformation_ref_id"])

        # Audit fields
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        new = await supervisorNotes_collection.insert_one(data)
        created = await supervisorNotes_collection.find_one({"_id": new.inserted_id})

        return success_response(
            supervisor_note_helper(created),
            msg="Supervisor note creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear supervisor note: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_supervisor_notes():
    try:
        supervisor_notes = [
            supervisor_note_helper(s)
            async for s in supervisorNotes_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(supervisor_notes, msg="Lista de supervisor notes obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener supervisor notes: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_supervisor_note(id: str):
    try:
        supervisor_note = await supervisorNotes_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if supervisor_note:
            return success_response(
                supervisor_note_helper(supervisor_note),
                msg="Supervisor note encontrada"
            )
        return error_response(
            "Supervisor note no encontrada",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener supervisor note: {str(e)}")


@router.put("/{id}")
async def update_supervisor_note(id: str, supervisor_note: SupervisorNoteModel):
    try:
        data = supervisor_note.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # Audit field
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await supervisorNotes_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "Supervisor note no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await supervisorNotes_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            supervisor_note_helper(updated),
            msg="Supervisor note actualizada"
        )
    except Exception as e:
        return error_response(f"Error al actualizar supervisor note: {str(e)}")


@router.delete("/{id}")
async def delete_supervisor_note(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        supervisor_note = await supervisorNotes_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not supervisor_note:
            return error_response(
                "Supervisor note no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await supervisorNotes_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="Supervisor note eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar supervisor note: {str(e)}")


@router.get("/by-general-informacion/{generalInformation_id}")
async def get_supervisor_notes_by_general_information(generalInformation_id: str):
    try:
        generalInformation_oid = ObjectId(generalInformation_id)

        supervisor_notes = [
            supervisor_note_helper(s)
            async for s in supervisorNotes_collection.find({
                "generalInformation_ref_id": generalInformation_oid,
                "active": True
            })
        ]

        return success_response(
            supervisor_notes,
            msg=f"Supervisor notes de la general_information {generalInformation_id} obtenidas"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener supervisor notes por general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )