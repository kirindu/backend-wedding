from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.auth import decode_token
from config.database import users_collection, employees_collection
from bson import ObjectId

# Cambiar de OAuth2PasswordBearer a HTTPBearer para soportar Authorization: Bearer
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):

    token = credentials.credentials
    
    try:
        # Decodificar el token
        payload = decode_token(token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        

        identifier = payload.get("sub")
        
        if not identifier:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        
        # ✅ Intentar buscar primero en users (por email)
        user = await users_collection.find_one({"email": identifier})
        
        if user:
            return {
                "id": str(user["_id"]),
                "name": user.get("name"),
                "email": user.get("email"),
                "rol": user.get("rol", "Admin"),
                "type": "user"
            }
        
        # ✅ Si no se encuentra en users, buscar en employee (por email)
        employee = await employees_collection.find_one({"email": identifier})
        
        if employee:
            return {
                "id": str(["_id"]),
                "name": employee.get("employeeName"),
                "email": employee.get("email"),
                "rol": employee.get("rol", "Employee"),
                "type": "Employee"
            }
        
        # Si no se encuentra en ninguna colección
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error de autenticación: {str(e)}"
        )