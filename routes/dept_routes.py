from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.dept_model import DeptModel

# Configuración de la base de datos y colecciones
from config.database import depts_collection

# Esquemas
from schemas.dept_scheme import dept_helper

# Rutas
router = APIRouter()

# CRUD para Dept
@router.post("/")
async def create_dept(dept: DeptModel):
    try:
        data = dept.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await depts_collection.insert_one(data)
        created = await depts_collection.find_one({"_id": new.inserted_id})
        return success_response(dept_helper(created), msg="Dept creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el dept: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_depts():
    try:
        depts = [dept_helper(dept) async for dept in depts_collection.find().sort("deptName", 1)]
        return success_response(depts, msg="Lista de depts obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los depts: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_dept(id: str):
    dept = await depts_collection.find_one({"_id": ObjectId(id)})
    if dept:
        return success_response(dept_helper(dept), msg="Dept encontrado")
    return error_response("Dept no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_dept(id: str, dept: DeptModel):
    update_data = dept.model_dump()
    update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

    res = await depts_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
    if res.matched_count == 0:
        return error_response("Dept no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await depts_collection.find_one({"_id": ObjectId(id)})
    return success_response(dept_helper(updated), msg="Dept actualizado")

@router.delete("/{id}")
async def delete_dept(id: str):
    """
    Soft delete a dept by setting active=False
    ❌ Ya NO es un hard delete
    """
    try:
        # Verificar que el dept existe y está activo
        dept = await depts_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not dept:
            return error_response(
                "Dept no encontrado o ya fue eliminado", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 🆕 Soft delete: marcar como inactivo
        await depts_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="Dept eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar dept: {str(e)}")

# @router.delete("/{id}")
# async def delete_dept(id: str):
#     res = await depts_collection.delete_one({"_id": ObjectId(id)})
#     if res.deleted_count:
#         return success_response(None, msg="Dept eliminado")
#     return error_response("Dept no encontrado", status_code=status.HTTP_404_NOT_FOUND)    