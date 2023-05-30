import os
import pickle
import io
import sys

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from modules.logger import Logger
from modules.utils import get_file_mimetype
import modules.utils as utils



log = Logger()

DEFAULT_FOLDER_NAME = "default-from-desk"
MAIN_PATH = os.getcwd()

def upload_file(file_path, folder_name):
    drive_service = utils.authenticate()
    os.chdir(MAIN_PATH)
    results = drive_service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'", spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        log.warn(f"No se encontró ninguna carpeta con el nombre {folder_name}")
        log.warn(f"Creando nueva carpeta con el nombre {folder_name}")
        file_metadata = {'name': folder_name, 'mimeType': 'application/vnd.google-apps.folder'}
        file = drive_service.files().create(body=file_metadata, fields='id').execute()
        folder_id = file.get('id')
        log.info(f"Carpeta creada!")
    else:
        folder_id = items[0]['id']
    log.log(f"Carpeta encontrada. (ID: {folder_id})")

    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    try:
        media = MediaIoBaseUpload(io.FileIO(file_path, 'rb'), mimetype=f"{get_file_mimetype(file_path)}", chunksize=1024*1024, resumable=True)
        log.warn(f"Subiendo el archivo {os.path.basename(file_path)} a la carpeta '{folder_name}'...")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        log.log(f"Archivo subido con exito!! (ID: {file.get('id')})")
    except FileNotFoundError:
        log.error(f"Archivo no encontrado: {file_path}")
        sys.exit(1)
