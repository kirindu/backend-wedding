from fastapi import APIRouter, status, UploadFile, File, Form, HTTPException
from models.load_model import LoadModel
from config.database import loads_collection
from schemas.load_scheme import load_helper
from utils.coversheet_updater import add_entity_to_coversheet
from utils.response_helper import success_response, error_response

from bson import ObjectId
from typing import List, Optional
import os
import uuid

router = APIRouter()

@router.post("/")
async def create_load_with_images(
    firstStopTime: Optional[str] = Form(None),
    route: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    coversheet_id: str = Form(...),
    images: List[UploadFile] = File(default=[])
):
    try:
        image_paths = []
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            if not image.content_type.startswith("image/"):
                return error_response(
                    f"El archivo '{image.filename}' no es una imagen válida.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            contents = await image.read()
            if len(contents) > 1 * 1024 * 1024:
                return error_response(
                    f"El archivo '{image.filename}' excede el tamaño máximo permitido de 1 MB.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            filename = f"{uuid.uuid4()}_{image.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            image_paths.append(file_path)

        data = {
            "firstStopTime": firstStopTime,
            "route": route,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "landFill": landFill,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths
        }

        new = await loads_collection.insert_one(data)
        created = await loads_collection.find_one({"_id": new.inserted_id})
        await add_entity_to_coversheet(coversheet_id, "load_id", str(new.inserted_id))

        return success_response(load_helper(created), msg="Load creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear load: {str(e)}")


@router.put("/{id}")
async def update_load_with_form(
    id: str,
    firstStopTime: Optional[str] = Form(None),
    route: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    images: List[UploadFile] = File(default=[])
):
    try:
        existing = await loads_collection.find_one({"_id": ObjectId(id)})
        if not existing:
            return error_response("Load no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        image_paths = existing.get("images", [])
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            if not image.content_type.startswith("image/"):
                return error_response(
                    f"El archivo '{image.filename}' no es una imagen válida.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            contents = await image.read()
            if len(contents) > 1 * 1024 * 1024:
                return error_response(
                    f"El archivo '{image.filename}' excede el tamaño máximo permitido de 1 MB.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            filename = f"{uuid.uuid4()}_{image.filename}"
            file_path = os.path.join(upload_dir, filename)
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
            image_paths.append(file_path)

        data = {
            "firstStopTime": firstStopTime,
            "route": route,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "landFill": landFill,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths
        }

        res = await loads_collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        updated = await loads_collection.find_one({"_id": ObjectId(id)})
        return success_response(load_helper(updated), msg="Load actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar load: {str(e)}")


@router.get("/")
async def get_all_loads():
    try:
        loads = [load_helper(load) async for load in loads_collection.find()]
        return success_response(loads, msg="Lista de loads obtenida")
    except Exception as e:
        return error_response(f"Error al obtener loads: {str(e)}")


@router.get("/{id}")
async def get_load(id: str):
    try:
        load = await loads_collection.find_one({"_id": ObjectId(id)})
        if load:
            return success_response(load_helper(load), msg="Load encontrada")
        return error_response("Load no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener load: {str(e)}")


@router.delete("/{id}")
async def delete_load(id: str):
    try:
        res = await loads_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Load eliminada")
        return error_response("Load no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar load: {str(e)}")
