from fastapi import APIRouter, HTTPException, status, Form
from fastapi.responses import JSONResponse
from utils.response_helper import success_response, error_response
from models.landfill_model import LandFillModel
from config.database import landfills_collection
from schemas.landfill_scheme import landfill_helper
from bson import ObjectId

router = APIRouter()

 
@router.post("/")
async def create_landfill(landfill: LandFillModel):
    try:
        new = await landfills_collection.insert_one(landfill.model_dump())
        created = await landfills_collection.find_one({"_id": new.inserted_id})
        return success_response(landfill_helper(created), msg="Landfill creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear el landfill: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/")
async def get_all_landfills():
    try:
        landfills = [landfill_helper(landfill) async for landfill in landfills_collection.find().sort("landfillName", 1)]
        return success_response(landfills, msg="Lista de landfills obtenida")
    except Exception as e:
        return error_response(f"Error al obtener los landfills: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_landfill(id: str):
    landfill = await landfills_collection.find_one({"_id": ObjectId(id)})
    if landfill:
        return success_response(landfill_helper(landfill), msg="Landfill encontrado")
    return error_response("Landfill no encontrado", status_code=status.HTTP_404_NOT_FOUND)

@router.put("/{id}")
async def update_landfill(id: str, landfill: LandFillModel):
    res = await landfills_collection.update_one({"_id": ObjectId(id)}, {"$set": landfill.model_dump()})
    if res.matched_count == 0:
        return error_response("LandFill no encontrado", status_code=status.HTTP_404_NOT_FOUND)

    updated = await landfills_collection.find_one({"_id": ObjectId(id)})
    return success_response(landfill_helper(updated), msg="Landfill actualizado")

@router.delete("/{id}")
async def delete_landfill(id: str):
    res = await landfills_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return success_response(None, msg="Landfill eliminado")
    return error_response("Landfill no encontrado", status_code=status.HTTP_404_NOT_FOUND)    