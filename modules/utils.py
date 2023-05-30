import mimetypes
import sys

import os
import pickle
import io

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

from modules.logger import Logger

log = Logger()


SCOPES = ["https://www.googleapis.com/auth/drive"]
DEFAULT_FOLDER_NAME = "default-from-desk"
MAIN_PATH = os.getcwd()

def authenticate():
    SERVICE_ACCOUNT_FILE = "credentials.json"
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            os.chdir(MAIN_PATH)
            flow = InstalledAppFlow.from_client_secrets_file(SERVICE_ACCOUNT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    drive_service = build('drive', 'v3', credentials=creds)
    return drive_service


def convert_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.2f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.2f} MB"
    else:
        return f"{size_bytes/1024**3:.2f} GB"

def get_file_mimetype(file_path):
    try:
        mimetype, _ = mimetypes.guess_type(file_path)
        return mimetype
    except FileNotFoundError:
        log.error(f"Archivo no encontrado: {file_path}")
        sys.exit(1)

def is_valid_file_id(file_id):
    service = authenticate()
    try:
        result = service.files().get(fileId=file_id, fields='id').execute()
        return True
    except:
        return False

def get_folder_id(folder_name, parent_id):
    service = authenticate()
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces='drive', pageSize=1, fields='files(id)').execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']
    else:
        return None

def search_file_by_id(file_id):
    service = authenticate()
    if not is_valid_file_id(file_id):
        log.error("ID de archivo inválido.")
        return
    try:
        result = service.files().get(fileId=file_id).execute()
        log.info(f"Archivo encontrado!")
        log.log(f"Nombre: {result['name']}")
        log.log(f"ID: {result['id']}")
        log.log(f"Tipo de archivo: {result['mimeType']}")
        log.log(f"Tamaño: {result['size']} bytes")
    except:
        log.error("No se pudo mostrar alguna propiedad del archivo.")

def list_files_in_folder(folder_name):
    service = authenticate()
    # Buscar la carpeta por su nombre
    folder_results = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'", spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folder_items = folder_results.get('files', [])

    if not folder_items:
        log.info(f"No se encontró ninguna carpeta con el nombre {folder_name}")
        return

    folder_id = folder_items[0]['id']
    log.info(f"Carpeta encontrada. (ID: {folder_id})")

    # Listar archivos dentro de la carpeta
    file_results = service.files().list(q=f"'{folder_id}' in parents", spaces='drive', pageSize=10, fields="nextPageToken, files(id, name, webViewLink, fileExtension, mimeType, size)").execute()
    file_items = file_results.get('files', [])

    if not file_items:
        log.info("No se encontraron archivos dentro de la carpeta.")
        return

    log.info(f"Archivos encontrados dentro de la carpeta '{folder_name}':")
    
    try:
        for file in file_items:
            name = file['name']
            size = convert_size(float(file['size'])) if 'size' in file else "'No Disponible'"
            id = file['id']
            log.log(f"Nombre: {name} | Tamaño: {size} | ID: {id}")
    except:
        log.error("No se pudo mostrar alguna propiedad del archivo.")
        pass

def list_folders():
    service = authenticate()
    # Buscar la carpeta por su nombre
    folder_results = service.files().list(q=f"mimeType='application/vnd.google-apps.folder' and trashed=false and 'root' in parents", spaces='drive', pageSize=10, fields="nextPageToken, files(id, name)").execute()
    folder_items = folder_results.get('files', [])

    if not folder_items:
        log.error(f"No se encontró nada")
        return
    log.info(f"Se encontraron {len(folder_items)} items")
    for folder in folder_items:
        log.info(f"Nombre: {folder['name']} | ID: {folder['id']}")

def navigate_folders(folder_path):
    folders = folder_path.split('/')
    current_folder_id = 'root'
    service = authenticate()

    for folder_name in folders:
        if folder_name == '':
            continue
        folder_id = get_folder_id(folder_name, current_folder_id)
        if folder_id:
            current_folder_id = folder_id
        else:
            log.error(f"No se encontró la carpeta '{folder_name}' en el directorio actual.")
            return

    results = service.files().list(q=f"'{current_folder_id}' in parents", spaces='drive', pageSize=10, fields="files(name, id)").execute()
    files = results.get('files', [])
    
    log.info(f"Archivos en la carpeta '{folder_path}':")
    if files:
        for file in files:
            log.log(f"Nombre: {file['name']} | ID: {file['id']}")
    else:
        log.error("No se encontraron archivos en esta carpeta.")