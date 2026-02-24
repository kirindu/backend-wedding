# Librerias
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo
from bson import ObjectId

# Modelos
from models.employeesignature_model import EmployeeSignatureModel  # ⚠️ Asegúrate de renombrar la clase en el modelo

# Configuración de la base de datos y colecciones
from config.database import employeeSignatures_collection

# Esquemas
from schemas.employeesignature_scheme import employee_signature_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_employee_signature(employee_signature: EmployeeSignatureModel):
    try:
        data = employee_signature.model_dump()

        # Convertir generalInformation_ref_id a ObjectId
        if data.get("generalInformation_ref_id"):
            data["generalInformation_ref_id"] = ObjectId(data["generalInformation_ref_id"])

        # Audit fields
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None
        data["active"] = data.get("active", True)

        new = await employeeSignatures_collection.insert_one(data)
        created = await employeeSignatures_collection.find_one({"_id": new.inserted_id})

        return success_response(
            employee_signature_helper(created),
            msg="Employee signature creada exitosamente"
        )
    except Exception as e:
        return error_response(
            f"Error al crear employee signature: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/")
async def get_all_employee_signatures():
    try:
        employee_signatures = [
            employee_signature_helper(e)
            async for e in employeeSignatures_collection.find({"active": True}).sort("createdAt", -1)
        ]
        return success_response(employee_signatures, msg="Lista de employee signatures obtenida")
    except Exception as e:
        return error_response(
            f"Error al obtener employee signatures: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get("/{id}")
async def get_employee_signature(id: str):
    try:
        employee_signature = await employeeSignatures_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if employee_signature:
            return success_response(
                employee_signature_helper(employee_signature),
                msg="Employee signature encontrada"
            )
        return error_response(
            "Employee signature no encontrada",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener employee signature: {str(e)}")


@router.put("/{id}")
async def update_employee_signature(id: str, employee_signature: EmployeeSignatureModel):
    try:
        data = employee_signature.model_dump(exclude_unset=True)

        # No permitir cambiar active a través de este endpoint
        data.pop("active", None)

        # Audit field
        data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await employeeSignatures_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )

        if res.matched_count == 0:
            return error_response(
                "Employee signature no encontrada o no está activa",
                status_code=status.HTTP_404_NOT_FOUND
            )

        updated = await employeeSignatures_collection.find_one({"_id": ObjectId(id)})
        return success_response(
            employee_signature_helper(updated),
            msg="Employee signature actualizada"
        )
    except Exception as e:
        return error_response(f"Error al actualizar employee signature: {str(e)}")


@router.delete("/{id}")
async def delete_employee_signature(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        employee_signature = await employeeSignatures_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not employee_signature:
            return error_response(
                "Employee signature no encontrada o ya fue eliminada",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await employeeSignatures_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="Employee signature eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar employee signature: {str(e)}")


@router.get("/by-general-informacion/{generalInformation_id}")
async def get_employee_signatures_by_general_information(generalInformation_id: str):
    try:
        generalInformation_oid = ObjectId(generalInformation_id)

        employee_signatures = [
            employee_signature_helper(e)
            async for e in employeeSignatures_collection.find({
                "generalInformation_ref_id": generalInformation_oid,
                "active": True
            })
        ]

        return success_response(
            employee_signatures,
            msg=f"Employee signatures de la general_information {generalInformation_id} obtenidas"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener employee signatures por general information: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )