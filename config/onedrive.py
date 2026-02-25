"""
OneDrive Upload Helper — Microsoft Graph API
Usa Client Credentials Flow con MSAL para caché automático de tokens.

Variables requeridas en .env:
    MS_GRAPH_CLIENT_ID
    MS_GRAPH_TENANT_ID
    MS_GRAPH_CLIENT_SECRET
    MS_GRAPH_USER_ID          ← Email o ID del usuario dueño del OneDrive (ej: admin@acedisposal.com)
    MS_GRAPH_UPLOAD_FOLDER    ← Carpeta destino en OneDrive (ej: ACE-Safety/uploads)
"""

import os
import uuid
import msal
import httpx
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID     = os.getenv("MS_GRAPH_CLIENT_ID")
TENANT_ID     = os.getenv("MS_GRAPH_TENANT_ID")
CLIENT_SECRET = os.getenv("MS_GRAPH_CLIENT_SECRET")
USER_ID       = os.getenv("MS_GRAPH_USER_ID")
UPLOAD_FOLDER = os.getenv("MS_GRAPH_UPLOAD_FOLDER", "ACE-Safety/uploads")

AUTHORITY     = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE         = ["https://graph.microsoft.com/.default"]
GRAPH_BASE    = "https://graph.microsoft.com/v1.0"

# ✅ Instancia única de MSAL — el caché de tokens vive aquí
# Se crea una sola vez cuando el módulo se importa, no en cada request
_msal_app = msal.ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)


def get_access_token() -> str:
    """
    Obtiene token de acceso usando el caché de MSAL.
    Solo hace una petición real a Microsoft cuando el token expira (~1 hora).
    """
    # Primero intenta obtener token del caché
    result = _msal_app.acquire_token_silent(SCOPE, account=None)

    # Si no hay token en caché, solicita uno nuevo
    if not result:
        result = _msal_app.acquire_token_for_client(scopes=SCOPE)

    if "access_token" in result:
        return result["access_token"]

    raise Exception(f"Error obteniendo token de Microsoft: {result.get('error_description', result.get('error'))}")


async def upload_file_to_onedrive(file_bytes: bytes, original_filename: str, subfolder: str = "") -> str:
    """
    Sube archivos de hasta 4MB a OneDrive con un PUT directo.
    Retorna la webUrl del archivo subido.
    """
    token = get_access_token()

    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    folder_path = f"{UPLOAD_FOLDER}/{subfolder}".strip("/") if subfolder else UPLOAD_FOLDER
    upload_path = f"{folder_path}/{unique_filename}"

    upload_url = f"{GRAPH_BASE}/users/{USER_ID}/drive/root:/{upload_path}:/content"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/octet-stream",
    }

    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url, content=file_bytes, headers=headers)
        response.raise_for_status()
        return response.json().get("webUrl", "")


async def upload_large_file_to_onedrive(file_bytes: bytes, original_filename: str, subfolder: str = "") -> str:
    """
    Sube archivos mayores a 4MB usando Upload Session (chunks de 5MB).
    Retorna la webUrl del archivo subido.
    """
    token = get_access_token()

    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    folder_path = f"{UPLOAD_FOLDER}/{subfolder}".strip("/") if subfolder else UPLOAD_FOLDER
    upload_path = f"{folder_path}/{unique_filename}"

    # 1. Crear upload session
    session_url = f"{GRAPH_BASE}/users/{USER_ID}/drive/root:/{upload_path}:/createUploadSession"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json"
    }

    async with httpx.AsyncClient() as client:
        session_resp = await client.post(session_url, json={
            "item": {"@microsoft.graph.conflictBehavior": "rename"}
        }, headers=headers)
        session_resp.raise_for_status()
        upload_session_url = session_resp.json()["uploadUrl"]

    # 2. Subir en chunks de 5MB
    chunk_size = 5 * 1024 * 1024
    file_size  = len(file_bytes)
    offset     = 0
    item       = {}

    async with httpx.AsyncClient() as client:
        while offset < file_size:
            chunk     = file_bytes[offset: offset + chunk_size]
            chunk_end = offset + len(chunk) - 1

            chunk_headers = {
                "Content-Length": str(len(chunk)),
                "Content-Range":  f"bytes {offset}-{chunk_end}/{file_size}",
            }

            resp = await client.put(upload_session_url, content=chunk, headers=chunk_headers)
            resp.raise_for_status()

            if resp.status_code in (200, 201):
                item = resp.json()

            offset += chunk_size

    return item.get("webUrl", "")


async def smart_upload(file_bytes: bytes, original_filename: str, subfolder: str = "") -> str:
    """
    Decide automáticamente entre upload simple o por chunks según el tamaño.
    Umbral: 4MB
    """
    if len(file_bytes) > 4 * 1024 * 1024:
        return await upload_large_file_to_onedrive(file_bytes, original_filename, subfolder)
    return await upload_file_to_onedrive(file_bytes, original_filename, subfolder)