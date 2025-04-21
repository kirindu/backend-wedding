from fastapi import APIRouter, HTTPException, status, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from auth import verify_password, create_access_token
from datetime import timedelta
from models.user_model import UserModel
from config.database import users_collection
from schemas.user_scheme import user_helper
from bson import ObjectId
from auth import hash_password
from dependencies import get_current_user

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas")
    
    access_token = create_access_token(data={"sub": user["email"]}, expires_delta=timedelta(minutes=60))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/")
async def create_user(user: UserModel):
    user_dict = user.model_dump()
    user_dict["password"] = hash_password(user_dict["password"])  # 👈 encriptar la contraseña

    new = await users_collection.insert_one(user_dict)
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
   res = await users_collection.update_one({"_id": ObjectId(id)}, {"$set": user.model_dump()})
   if res.matched_count == 0:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
   updated = await users_collection.find_one({"_id": ObjectId(id)})
   return user_helper(updated)


# Eliminar un usuario solo si el rol del usuario actual es "Admin" siempre que el token sea válido
@router.delete("/{id}")
async def delete_user(id: str, current_user: dict = Depends(get_current_user)):
    if current_user.get("rol") != "Admin":
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar usuarios")

    res = await users_collection.delete_one({"_id": ObjectId(id)})
    if res.deleted_count:
        return {"msg": "User deleted"}
    raise HTTPException(404, detail="User not found")