from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, status
from utils.response_helper import success_response, error_response
from bson import ObjectId

# Modelos
from models.whodidyousendthepictureto_model import WhoDidYouSendThePictureToModel

# Configuración de la base de datos y colecciones
from config.database import whoDidYouSendThePicturesTo_collection
# Esquemas
from schemas.whodidyousendthepictureto_scheme import who_did_you_send_the_picture_to_helper

# Rutas
router = APIRouter()


@router.post("/")
async def create_who_did_you_send_the_picture_to(who_did_you_send_the_picture_to: WhoDidYouSendThePictureToModel):
    try:
        data = who_did_you_send_the_picture_to.model_dump()
        data["createdAt"] = datetime.now(ZoneInfo("America/Denver"))
        data["updatedAt"] = None

        new = await whoDidYouSendThePicturesTo_collection.insert_one(data)
        created = await whoDidYouSendThePicturesTo_collection.find_one({"_id": new.inserted_id})
        return success_response(who_did_you_send_the_picture_to_helper(created), msg="Who did you send the picture to creado exitosamente")
    except Exception as e:
        return error_response(f"Error al crear who did you send the picture to: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/")
async def get_all_who_did_you_send_the_picture_to():
    try:
        result = [
            who_did_you_send_the_picture_to_helper(w)
            async for w in whoDidYouSendThePicturesTo_collection.find({"active": True}).sort("whoDidYouSendThePictureToName", 1)
        ]
        return success_response(result, msg="Lista de who did you send the picture to obtenida")
    except Exception as e:
        return error_response(f"Error al obtener who did you send the picture to: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/{id}")
async def get_who_did_you_send_the_picture_to(id: str):
    try:
        who_did_you_send_the_picture_to = await whoDidYouSendThePicturesTo_collection.find_one({"_id": ObjectId(id)})
        if who_did_you_send_the_picture_to:
            return success_response(who_did_you_send_the_picture_to_helper(who_did_you_send_the_picture_to), msg="Who did you send the picture to encontrado")
        return error_response("Who did you send the picture to no encontrado", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener who did you send the picture to: {str(e)}")


@router.put("/{id}")
async def update_who_did_you_send_the_picture_to(id: str, who_did_you_send_the_picture_to: WhoDidYouSendThePictureToModel):
    try:
        update_data = who_did_you_send_the_picture_to.model_dump()
        update_data["updatedAt"] = datetime.now(ZoneInfo("America/Denver"))

        res = await whoDidYouSendThePicturesTo_collection.update_one({"_id": ObjectId(id)}, {"$set": update_data})
        if res.matched_count == 0:
            return error_response("Who did you send the picture to no encontrado", status_code=status.HTTP_404_NOT_FOUND)

        updated = await whoDidYouSendThePicturesTo_collection.find_one({"_id": ObjectId(id)})
        return success_response(who_did_you_send_the_picture_to_helper(updated), msg="Who did you send the picture to actualizado")
    except Exception as e:
        return error_response(f"Error al actualizar who did you send the picture to: {str(e)}")


@router.delete("/{id}")
async def delete_who_did_you_send_the_picture_to(id: str):
    """Soft delete - marca como inactivo en lugar de eliminar"""
    try:
        who_did_you_send_the_picture_to = await whoDidYouSendThePicturesTo_collection.find_one({
            "_id": ObjectId(id),
            "active": True
        })

        if not who_did_you_send_the_picture_to:
            return error_response(
                "Who did you send the picture to no encontrado o ya fue eliminado",
                status_code=status.HTTP_404_NOT_FOUND
            )

        await whoDidYouSendThePicturesTo_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"active": False, "updatedAt": datetime.now(ZoneInfo("America/Denver"))}}
        )

        return success_response(None, msg="Who did you send the picture to eliminado (soft delete)")
    except Exception as e:
        return error_response(f"Error al eliminar who did you send the picture to: {str(e)}")