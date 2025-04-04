from fastapi import APIRouter, HTTPException
from models.user_model import UserModel
from config.database import users_collection
from schemas.user_scheme import user_helper
from bson import ObjectId

router = APIRouter()

@router.post("/")
async def create_user(user: UserModel):
    new = await users_collection.insert_one(user.dict())
    created = await users_collection.find_one({"_id": new.inserted_id})
    return user_helper(created)

@router.get("/")
async def get_all_users():
    return [user_helper(user) async for user in users_collection.find()]

@router.get("/{id}")
async def get_user(id: str):
    user = await users_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)
    raise HTTPException(404, detail="User not found")

@router.put("/{id}")
async def update_user(id: str, user: UserModel):
    await users_collection.update_one({"_id": ObjectId(id)}, {"$set": user.dict()})
    updated = await users_collection.find_one({"_id": ObjectId(id)})
    return user_helper(updated)


@router.delete("/{id}")
async def delete_user(id: str):
    res = await users_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "User deleted"}
    raise HTTPException(404, detail="User not found")
