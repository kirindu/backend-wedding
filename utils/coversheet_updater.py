from bson import ObjectId
from config.database import coversheets_collection
from fastapi import HTTPException

async def add_entity_to_coversheet(coversheet_id: str, entity_field: str, entity_id: str):
    """
    Agrega un ID de entidad a un campo específico del Coversheet (como 'load_id' o 'spareTruckInfo_id').
    
    :param coversheet_id: ID del coversheet que se actualizará.
    :param entity_field: Campo del coversheet al que se agregará el ID ('load_id', 'spareTruckInfo_id', etc).
    :param entity_id: ID de la entidad recién creada.
    """
    coversheet = await coversheets_collection.find_one({"_id": ObjectId(coversheet_id)})
    if not coversheet:
        raise HTTPException(status_code=404, detail="Coversheet no encontrado")

    await coversheets_collection.update_one(
        {"_id": ObjectId(coversheet_id)},
        {"$push": {entity_field: entity_id}}
    )
