from fastapi.responses import JSONResponse
from fastapi import status

def success_response(data=None, msg="Operación exitosa", status_code=status.HTTP_200_OK):
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": True,
            "msg": msg,
            "data": data
        }
    )

def error_response(msg="Ocurrió un error", status_code=status.HTTP_400_BAD_REQUEST):
    return JSONResponse(
        status_code=status_code,
        content={
            "ok": False,
            "msg": msg,
            "data": None
        }
    )