from fastapi import APIRouter, status
from models.downtime_model import DowntimeModel
from config.database import downtimes_collection
from config.database import trucks_collection 
from schemas.downtime_scheme import downtime_helper
from utils.coversheet_updater import add_entity_to_coversheet
from utils.response_helper import success_response, error_response

from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_downtime(downtime: DowntimeModel):
    try:
        data = downtime.model_dump()
        coversheet_id = data.pop("coversheet_id")
        
         # 🔍 Agregar truckNumber a partir del route_id
        truck_id = data.get("truck_id")
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        new = await downtimes_collection.insert_one(data)
        created = await downtimes_collection.find_one({"_id": new.inserted_id})

        await add_entity_to_coversheet(coversheet_id, "downtime_id", str(new.inserted_id))

        return success_response(downtime_helper(created), msg="Downtime creada exitosamente")
    except Exception as e:
        return error_response(f"Error al crear downtime: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)






@router.get("/")
async def get_all_downtimes():
    try:
        downtimes = [downtime_helper(d) async for d in downtimes_collection.find()]
        return success_response(downtimes, msg="Lista de downtimes obtenida")
    except Exception as e:
        return error_response(f"Error al obtener downtimes: {str(e)}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{id}")
async def get_downtime(id: str):
    try:
        downtime = await downtimes_collection.find_one({"_id": ObjectId(id)})
        if downtime:
            return success_response(downtime_helper(downtime), msg="Downtime encontrada")
        return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al obtener downtime: {str(e)}")
    
@router.put("/{id}")
async def update_downtime(id: str, downtime: DowntimeModel):
    try:
        data = downtime.model_dump()

        # 🔄 Obtener el nuevo truck_id y buscar el truckNumber correspondiente
        truck_id = data.get("truck_id")
        if truck_id:
            truck_doc = await trucks_collection.find_one({"_id": ObjectId(truck_id)})
            if truck_doc and truck_doc.get("truckNumber"):
                data["truckNumber"] = truck_doc["truckNumber"]

        # 🛠️ Actualizar el documento
        res = await downtimes_collection.update_one({"_id": ObjectId(id)},{"$set": data})

        if res.matched_count == 0:
            return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)

        updated = await downtimes_collection.find_one({"_id": ObjectId(id)})
        return success_response(downtime_helper(updated), msg="Downtime actualizada")
    except Exception as e:
        return error_response(f"Error al actualizar downtime: {str(e)}")
    

# @router.put("/{id}")
# async def update_downtime(id: str, downtime: DowntimeModel):
#     try:
#         res = await downtimes_collection.update_one({"_id": ObjectId(id)}, {"$set": downtime.model_dump()})
#         if res.matched_count == 0:
#             return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)
#         updated = await downtimes_collection.find_one({"_id": ObjectId(id)})
#         return success_response(downtime_helper(updated), msg="Downtime actualizada")
#     except Exception as e:
#         return error_response(f"Error al actualizar downtime: {str(e)}")

@router.delete("/{id}")
async def delete_downtime(id: str):
    try:
        res = await downtimes_collection.delete_one({"_id": ObjectId(id)})
        if res.deleted_count:
            return success_response(None, msg="Downtime eliminada")
        return error_response("Downtime no encontrada", status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return error_response(f"Error al eliminar downtime: {str(e)}")
