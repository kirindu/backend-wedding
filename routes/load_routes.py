from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from models.load_model import LoadModel
from config.database import loads_collection
from schemas.load_scheme import load_helper
from bson import ObjectId
from typing import List, Optional
import os
import shutil
import uuid
from utils.coversheet_updater import add_entity_to_coversheet


router = APIRouter()

# Si te fijas he agregado coversheet_id como refencia a coversheet
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
    image_paths = []

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    for image in images:
        # Validar tipo de archivo (MIME)
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"El archivo '{image.filename}' no es una imagen válida."
            )

        # Validar tamaño del archivo (máximo 1 MB)
        contents = await image.read()
        if len(contents) > 1 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo '{image.filename}' excede el tamaño máximo permitido de 1 MB."
            )

        # Guardar archivo
        filename = f"{uuid.uuid4()}_{image.filename}"
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        image_paths.append(file_path)

    # Guardamos los datos
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
        "images": image_paths  # guardamos las rutas de las imágenes
    }

    new = await loads_collection.insert_one(data)
    created = await loads_collection.find_one({"_id": new.inserted_id})
    
    # Asociar con Coversheet
    await add_entity_to_coversheet(coversheet_id, "load_id", str(new.inserted_id))

    
    return load_helper(created)

@router.get("/")
async def get_all_loads():
    return [load_helper(load) async for load in loads_collection.find()]

@router.get("/{id}")
async def get_load(id: str):
    load = await loads_collection.find_one({"_id": ObjectId(id)})
    if load:
        return load_helper(load)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")

@router.put("/{id}")
async def update_load(id: str, load: LoadModel):
    res = await loads_collection.update_one({"_id": ObjectId(id)}, {"$set": load.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")
    updated = await loads_collection.find_one({"_id": ObjectId(id)})
    return load_helper(updated)


@router.delete("/{id}")
async def delete_load(id: str):
    res = await loads_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "Load deleted"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")
