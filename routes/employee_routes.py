from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.employee_model import EmployeeModel
from config.database import employees_collection
from schemas.employee_scheme import employee_helper
from config.auth import verify_password, create_access_token, hash_password
from datetime import timedelta
from bson import ObjectId

router = APIRouter()

@router.post("/login")
async def employee_login(employee: EmployeeModel):
    try:
        db_employee = await employees_collection.find_one({"email": employee.email})

        if not db_employee or not verify_password(employee.password, db_employee["password"]):
            return error_response("Credenciales inválidas", status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(
            data={"sub": db_employee["email"]}
        )

        employee_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(db_employee["_id"]),
                "name": db_employee["name"],
                "email": db_employee["email"],
                "rol": db_employee["rol"]
            }
        }

        return success_response(employee_data, msg="Login exitoso")

    except Exception as e:
        return error_response(f"Error interno al autenticar: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post("/")
async def create_employee(employee: EmployeeModel):
    try:
        employee_dict = employee.model_dump()
        employee_dict["password"] = hash_password(employee_dict["password"])
        employee_dict["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        employee_dict["updatedAt"] = None

        new = await employees_collection.insert_one(employee_dict)
        created = await employees_collection.find_one({"_id": new.inserted_id})
        return success_response(employee_helper(created), msg="Employee creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el employee: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_employees():
    try:
        employees = [employee_helper(employee) async for employee in employees_collection.find().sort("name", 1)]
        return success_response(employees, msg="Lista de employees obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los employees: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_employee(id: str):
    employee = await employees_collection.find_one({"_id": ObjectId(id)})
    if employee:
        return success_response(employee_helper(employee), msg="Employee encontrado")
    return error_response("Employee no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_employee(id: str, employee: EmployeeModel):
    try:
        employee_dict = employee.model_dump()
        employee_dict["password"] = hash_password(employee_dict["password"])
        employee_dict["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await employees_collection.update_one({"_id": ObjectId(id)}, {"$set": employee_dict})
        if res.matched_count == 0:
            return error_response("Employee no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await employees_collection.find_one({"_id": ObjectId(id)})
        return success_response(employee_helper(updated), msg="Employee actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar employee: {str(e)}")

@router.delete("/{id}")
async def delete_employee(id: str):
    """
    Soft delete an employee by setting active=False
    """
    try:
        employee = await employees_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not employee:
            return error_response(
                "Employee no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await employees_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )

        return success_response(None, msg="Employee eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar employee: {str(e)}")