from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.supervisor_model import SupervisorModel

# Configuración de la base de datos y colecciones
from config.database import supervisors_collection

# Esquemas
from schemas.supervisor_scheme import supervisor_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_supervisor(supervisor: SupervisorModel):
    try:
        data = supervisor.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await supervisors_collection.insert_one(data)
        created = await supervisors_collection.find_one({"_id": new.inserted_id})
        return success_response(supervisor_helper(created), msg="Supervisor creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear supervisor: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_supervisors():
    try:
        supervisors = [
            supervisor_helper(s)
            async for s in supervisors_collection.find({"active": True}).sort("supervisorName", 1)
        ]
        return success_response(supervisors, msg="Lista de supervisors obtenida")
    except Exception as e:
        return error_response(f"Error al obtener supervisors: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_supervisor(id: str):
    try:
        supervisor = await supervisors_collection.find_one({"_id": ObjectId(id)})
        if supervisor:
            return success_response(supervisor_helper(supervisor), msg="Supervisor encontrado")
        return error_response("Supervisor no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener supervisor: {str(e)}")


@router.put("/{id}")
async def update_supervisor(id: str, supervisor: SupervisorModel):
    try:
        update_data = supervisor.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await supervisors_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Supervisor no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await supervisors_collection.find_one({"_id": ObjectId(id)})
        return success_response(supervisor_helper(updated), msg="Supervisor actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar supervisor: {str(e)}")


@router.delete("/{id}")
async def delete_supervisor(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        supervisor = await supervisors_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not supervisor:
            return error_response(
                "Supervisor no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await supervisors_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Supervisor eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar supervisor: {str(e)}")