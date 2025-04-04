from fastapi import APIRouter, status, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse, StreamingResponse
from datetime import datetime
import os
import shutil
from uuid import uuid4

api = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Los métodos para enviar fotos se esperan que sean enviados como multipart/form-data

@api.post("/subida/", status_code=status.HTTP_200_OK)
async def subida(imagen: UploadFile = File(...)):
    if getExtension(imagen.content_type)=="no":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El archivo debe ser JPG o PNG")
    nombre = f"{datetime.timestamp(datetime.now())}{getExtension(imagen.content_type)}" # Le damos un nombre a la imagen
    file_name = os.getcwd() + "/uploads/" + nombre
    with open(file_name, 'wb+') as f:
        f.write(imagen.file.read())
        f.close()
    return {"mensaje": imagen}
    # Si queremos mostrar la imagen que subimos
    # return FileResponse(os.getcwd()+"/uploads/" + nombre)



@api.post("/upload/", tags=['Loads'])
async def upload_image(
    nombre: str = Form(...),
    direccion: str = Form(...),
    imagen: UploadFile = File(...)
):
    try:
        # Crear nombre único para el archivo
        filename = f"{uuid4().hex}_{imagen.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Guardar archivo en disco
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(imagen.file, buffer)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Archivo subido correctamente",
                "nombre": nombre,
                "direccion": direccion,
                "filename": filename,
                "filepath": file_path
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

def getExtension(content_type):
    if content_type == "image/png":
        return ".png"
    elif content_type == "image/jpg":
        return ".jpg"
    else:
        return "no"
