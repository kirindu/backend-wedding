from fastapi import APIRouter, status, UploadFile, File, Form, HTTPException
from models.load_model import LoadModel
from config.database import (
    loads_collection,
    routes_collection,
    landfills_collection,
    materials_collection
)
from schemas.load_scheme import load_helper
from utils.response_helper import success_response, error_response
from datetime import datetime
from zoneinfo import ZoneInfo

from bson import ObjectId
from typing import List, Optional
import os
import uuid

router = APIRouter()


@router.post("/")
async def create_load_with_images(
    firstStopTime: Optional[str] = Form(None),
    route_id: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill_id: Optional[str] = Form(None),
    material_id: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    coversheet_ref_id: str = Form(...),
    images: Optional[List[UploadFile]] = File(None)  # ✅ Cambiado para aceptar None
):
    """
    Create a new load with optional images
    Nueva estructura: Ya NO actualiza el array en coversheet,
    solo guarda la referencia coversheet_ref_id en el load
    """
    try:
        image_paths = []  # ✅ Siempre inicializa como array vacío
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # ✅ Procesar imágenes solo si existen Y no están vacías
        if images and len(images) > 0:
            # Verificar que el primer elemento no sea un archivo vacío
            first_file = images[0]
            if first_file.filename:  # ✅ Solo procesar si tiene nombre de archivo
                for image in images:
                    # Validar que sea una imagen
                    if not image.content_type.startswith("image/"):
                        return error_response(
                            f"The file '{image.filename}' is not an image.",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )

                    contents = await image.read()
                    
                    # Validar tamaño solo si tiene contenido
                    if len(contents) > 5 * 1024 * 1024:
                        return error_response(
                            f"The file '{image.filename}' exceeds the maximum size of 5MB.",
                            status_code=status.HTTP_400_BAD_REQUEST
                        )

                    # Guardar imagen
                    filename = f"{uuid.uuid4()}_{image.filename}"
                    file_path = os.path.join(upload_dir, filename)
                    with open(file_path, "wb") as buffer:
                        buffer.write(contents)
                    image_paths.append(file_path)

        # Preparar datos del load
        data = {
            "firstStopTime": firstStopTime,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths,  # ✅ Siempre será un array (vacío o con rutas)
            "createdAt": datetime.now(ZoneInfo("America/Denver")),
            "updatedAt": None
        }
        
        # 🆕 Convertir coversheet_ref_id a ObjectId
        if coversheet_ref_id:
            data["coversheet_ref_id"] = ObjectId(coversheet_ref_id)
        
        # 🆕 Establecer active en True
        data["active"] = True
        
        # Convertir route_id a ObjectId y obtener routeNumber
        if route_id:
            try:
                data["route_id"] = ObjectId(route_id)
                route_doc = await routes_collection.find_one({"_id": data["route_id"]})
                if route_doc and route_doc.get("routeNumber"):
                    data["routeNumber"] = route_doc["routeNumber"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar routeNumber: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )
        
        # Convertir landFill_id a ObjectId y obtener landfillName
        if landFill_id:
            try:
                data["landFill_id"] = ObjectId(landFill_id)
                landfill_doc = await landfills_collection.find_one({"_id": data["landFill_id"]})
                if landfill_doc and landfill_doc.get("landfillName"):
                    data["landfillName"] = landfill_doc["landfillName"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar landfillName: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Convertir material_id a ObjectId y obtener materialName
        if material_id:
            try:
                data["material_id"] = ObjectId(material_id)
                material_doc = await materials_collection.find_one({"_id": data["material_id"]})
                if material_doc and material_doc.get("materialName"):
                    data["materialName"] = material_doc["materialName"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar materialName: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Insertar el nuevo load
        new = await loads_collection.insert_one(data)
        created = await loads_collection.find_one({"_id": new.inserted_id})
        
        # ❌ Ya NO llamamos a add_entity_to_coversheet
        # El coversheet ya no mantiene arrays de IDs

        return success_response(load_helper(created), msg="Load created successfully")
    except Exception as e:
        return error_response(f"Error creating load: {str(e)}")


@router.put("/{id}")
async def update_load_with_form(
    id: str,
    firstStopTime: Optional[str] = Form(None),
    route_id: Optional[str] = Form(None),
    lastStopTime: Optional[str] = Form(None),
    landFillTimeIn: Optional[str] = Form(None),
    landFillTimeOut: Optional[str] = Form(None),
    grossWeight: Optional[float] = Form(None),
    tareWeight: Optional[float] = Form(None),
    tons: Optional[float] = Form(None),
    landFill_id: Optional[str] = Form(None),
    material_id: Optional[str] = Form(None),
    ticketNumber: Optional[str] = Form(None),
    note: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None)  # ✅ Cambiado para aceptar None
):
    """Update an existing active load with optional new images"""
    try:
        # 🆕 Solo actualizar si el load está activo
        existing = await loads_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not existing:
            return error_response(
                "Load not found or inactive", 
                status_code=status.HTTP_404_NOT_FOUND
            )

        # Mantener las imágenes existentes
        image_paths = existing.get("images", [])
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        # ✅ Agregar nuevas imágenes solo si existen Y no están vacías
        if images and len(images) > 0:
            first_file = images[0]
            if first_file.filename:  # ✅ Solo procesar si tiene nombre de archivo
                for image in images:
                    if not image.content_type.startswith("image/"):
                        return error_response(
                            f"El archivo '{image.filename}' no es una imagen válida.",
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

        # Preparar datos para actualización
        data = {
            "firstStopTime": firstStopTime,
            "lastStopTime": lastStopTime,
            "landFillTimeIn": landFillTimeIn,
            "landFillTimeOut": landFillTimeOut,
            "grossWeight": grossWeight,
            "tareWeight": tareWeight,
            "tons": tons,
            "ticketNumber": ticketNumber,
            "note": note,
            "images": image_paths,  # ✅ Siempre será un array
            "updatedAt": datetime.now(ZoneInfo("America/Denver"))
        }
        
        # 🆕 NO permitir cambiar coversheet_ref_id o active
        # Estos campos no deben ser modificados por este endpoint
        
        # Convertir route_id a ObjectId y obtener routeNumber
        if route_id:
            try:
                data["route_id"] = ObjectId(route_id)
                route_doc = await routes_collection.find_one({"_id": data["route_id"]})
                if route_doc and route_doc.get("routeNumber"):
                    data["routeNumber"] = route_doc["routeNumber"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar routeNumber: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Convertir landFill_id a ObjectId y obtener landfillName
        if landFill_id:
            try:
                data["landFill_id"] = ObjectId(landFill_id)
                landfill_doc = await landfills_collection.find_one({"_id": data["landFill_id"]})
                if landfill_doc and landfill_doc.get("landfillName"):
                    data["landfillName"] = landfill_doc["landfillName"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar landfillName: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Convertir material_id a ObjectId y obtener materialName
        if material_id:
            try:
                data["material_id"] = ObjectId(material_id)
                material_doc = await materials_collection.find_one({"_id": data["material_id"]})
                if material_doc and material_doc.get("materialName"):
                    data["materialName"] = material_doc["materialName"]
            except Exception as lookup_error:
                return error_response(
                    f"Error al buscar materialName: {str(lookup_error)}", 
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Actualizar solo si está activo
        res = await loads_collection.update_one(
            {"_id": ObjectId(id), "active": True},
            {"$set": data}
        )
        
        if res.matched_count == 0:
            return error_response(
                "Load not found or inactive",
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        updated = await loads_collection.find_one({"_id": ObjectId(id)})
        return success_response(load_helper(updated), msg="Load actualizada")
    except Exception as e:
        return error_response(f"Error updating load: {str(e)}")


@router.get("/")
async def get_all_loads():
    """Get all active loads"""
    try:
        # 🆕 Filtrar solo los activos
        loads = [
            load_helper(load) 
            async for load in loads_collection.find({"active": True})
        ]
        return success_response(loads, msg="Lista de loads obtenida")
    except Exception as e:
        return error_response(f"Error al obtener loads: {str(e)}")


@router.get("/{id}")
async def get_load(id: str):
    """Get a single active load by ID"""
    try:
        load = await loads_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        if load:
            return success_response(load_helper(load), msg="Load encontrada")
        return error_response(
            "Load no encontrada", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return error_response(f"Error al obtener load: {str(e)}")


@router.delete("/{id}")
async def delete_load(id: str):
    """
    Soft delete a load by setting active=False
    ❌ Ya NO es un hard delete
    """
    try:
        # Verificar que el load existe y está activo
        load = await loads_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })
        
        if not load:
            return error_response(
                "Load no encontrada o ya fue eliminada", 
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # 🆕 Soft delete: marcar como inactivo
        await loads_collection.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "active": False,
                    "updatedAt": datetime.now(ZoneInfo("America/Denver"))
                }
            }
        )
        
        return success_response(None, msg="Load eliminada (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar load: {str(e)}")


@router.get("/by-coversheet/{coversheet_id}")
async def get_loads_by_coversheet(coversheet_id: str):
    """
    🆕 Nuevo endpoint: Obtener todos los loads de un coversheet específico
    Útil para queries desde el frontend
    """
    try:
        coversheet_oid = ObjectId(coversheet_id)
        
        loads = [
            load_helper(load)
            async for load in loads_collection.find({
                "coversheet_ref_id": coversheet_oid,
                "active": True
            })
        ]
        
        return success_response(
            loads, 
            msg=f"Loads del coversheet {coversheet_id} obtenidos"
        )
    except Exception as e:
        return error_response(
            f"Error al obtener loads por coversheet: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )