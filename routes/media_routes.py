# Librerías
from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse
from utils.response_helper import error_response
import httpx

# Token MSAL desde el helper existente de OneDrive
from config.onedrive import get_access_token

# Rutas
router = APIRouter()


@router.get("/image-proxy")
async def image_proxy(url: str):
    """
    Proxy para servir imágenes privadas de OneDrive/SharePoint.
    El backend usa el token MSAL para autenticarse con Microsoft Graph
    y retorna la imagen directamente al frontend sin exponer credenciales.

    Uso desde el frontend:
        /api/media/image-proxy?url=<onedrive_url_encoded>
    """
    try:
        token = get_access_token()  # ✅ síncrono, sin await

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                follow_redirects=True
            )

            if response.status_code == 404:
                return error_response(
                    "Imagen no encontrada en OneDrive",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if response.status_code != 200:
                return error_response(
                    f"Error al obtener imagen de OneDrive: HTTP {response.status_code}",
                    status_code=status.HTTP_502_BAD_GATEWAY
                )

            content_type = response.headers.get("content-type", "image/jpeg")

            return StreamingResponse(
                iter([response.content]),
                media_type=content_type,
                headers={
                    # Cache de 1 hora en el navegador para no repetir requests innecesarios
                    "Cache-Control": "private, max-age=3600"
                }
            )

    except httpx.TimeoutException:
        return error_response(
            "Timeout al intentar obtener la imagen",
            status_code=status.HTTP_504_GATEWAY_TIMEOUT
        )
    except Exception as e:
        return error_response(
            f"Error en image proxy: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )