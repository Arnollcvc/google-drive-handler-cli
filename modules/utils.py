import os
import sys
import pickle
import mimetypes

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from tabulate import tabulate
from termcolor import colored

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

service = authenticate()

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
    try:
        result = service.files().get(fileId=file_id, fields='id').execute()
        return True
    except:
        return False

def get_folder_id(folder_name, parent_id):
    # service = authenticate()
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents"
    results = service.files().list(q=query, spaces='drive', pageSize=1, fields='files(id)').execute()
    folders = results.get('files', [])
    if folders:
        return folders[0]['id']
    else:
        return None

def search_item_by_id(file_id):
    # service = authenticate()
    if not is_valid_file_id(file_id):
        log.error("ID inválido.")
        return
    try:
        result = service.files().get(fileId=file_id).execute()
        log.info(f"Archivo encontrado!")
        log.log(f"Nombre: {result['name']}")
        log.log(f"ID: {result['id']}")
        log.log(f"Tipo de archivo: {result['mimeType']}")
        log.log(f"Tamaño: {result['size']} bytes")
    except:
        #log.error("No se pudo mostrar alguna propiedad del archivo.")
        pass

def find_by_id(file_id):
    if not is_valid_file_id(file_id):
        log.error("ID inválido.")
        return
    try:
        return service.files().get(fileId=file_id).execute()
    except:
        return False

def list_files_in_folder(folder_name):
    # service = authenticate()
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
    # service = authenticate()
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
    for folder_name in folders:
        if folder_name == '':
            continue
        folder_id = get_folder_id(folder_name, current_folder_id)
        if folder_id:
            current_folder_id = folder_id
        else:
            log.error(f"No se encontró la carpeta '{folder_name}' en el directorio actual.")
            return

    results = service.files().list(q=f"'{current_folder_id}' in parents", spaces='drive', pageSize=10, fields="files(name, id, mimeType)").execute()
    files = results.get('files', [])

    log.info(f"Archivos en la carpeta '{folder_path}':")
    if files:
        max_name_length = max(len(file['name'] + ' (' + file['mimeType'] + ')') for file in files)
        max_id_length = max(len(file['id']) for file in files)
        padding_name = '─' * ((max_name_length - len('Nombre')) // 2)
        padding_id = '─' * ((max_id_length - len('ID')) // 2)
        table_data = [[colored(file['name'], 'white', 'on_blue') + f" ({file['mimeType']})", colored(file['id'], 'white')] for file in files]
        table_headers = [colored(f"{padding_name} Nombre {padding_name}", 'white', 'on_magenta'), colored(f"{padding_id} ID {padding_id}", 'white', 'on_cyan')]
        table = tabulate(table_data, headers=table_headers, tablefmt='rounded_grid')
        print(table)
    else:
        log.error("No se encontraron archivos en esta carpeta.")


def get_folder_item_count(folder_id):
    try:
        count = 0
        page_size = 1000  # Tamaño de página grande para obtener todos los resultados
        page_token = None
        while True:
            results = service.files().list(q=f"'{folder_id}' in parents", spaces='drive', pageSize=page_size, pageToken=page_token, fields="nextPageToken, files(id)").execute()
            items = results.get('files', [])
            count += len(items)
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        return count
    except Exception as e:
        log.error(f"No se pudo obtener el número de elementos en la carpeta (ID: {folder_id}): {str(e)}")
        return None


def lfiles_in_folder(folder_id, folder_name=None, page_size=10):
    try:
        page_token = None
        file_counter = 0

        # Verificar la cantidad de elementos en la carpeta
        folder_item_count = get_folder_item_count(folder_id)

        # Si hay más de 100 elementos, preguntar al usuario
        if folder_item_count and folder_item_count > 100:
            answer = input(f"\033[93m[WARN]\033[0m Hay más de 100 elementos en la carpeta ({folder_item_count}). ¿Desea verlos de todos modos? (y/n): ")
            if answer.lower() != "y":
                return

        while True:
            if folder_name:
                query = f"'{folder_id}' in parents and name='{folder_name}'"
            else:
                query = f"'{folder_id}' in parents"

            results = service.files().list(q=query, spaces='drive', pageSize=page_size, pageToken=page_token, fields="nextPageToken, files(name, id, mimeType)").execute()
            files = results.get('files', [])
            page_token = results.get('nextPageToken')
            if files:
                max_name_length = max(len(file['name'] + ' (' + file['mimeType'] + ')') for file in files)
                max_id_length = max(len(file['id']) for file in files)
                padding_name = '─' * ((max_name_length - len('Nombre') - 2) // 2)
                padding_id = '─' * ((max_id_length - len('ID')) // 2)
                table_data = []
                for i, file in enumerate(files):
                    name = file['name']
                    if len(name) > 43:
                        name = name[:40] + '...'
                        extra_chars = len(file['name']) - 43
                        name += f" ({extra_chars} caracteres más)"
                    table_data.append([
                        colored(str(file_counter + i + 1), 'white', 'on_yellow'),
                        colored(name + f" ({file['mimeType']})", 'white', 'on_blue'),
                        colored(file['id'], 'white')
                    ])
                table_headers = [
                    colored(f"#", 'white', 'on_magenta'),
                    colored(f"{padding_name} Nombre {padding_name}", 'white', 'on_magenta'),
                    colored(f"{padding_id} ID {padding_id}", 'white', 'on_cyan')
                ]
                table = tabulate(table_data, headers=table_headers, tablefmt='rounded_grid')
                print(table)
                file_counter += len(files)
            else:
                log.info("No se encontraron archivos en esta carpeta.")
                break
            if not page_token:
                break
    except Exception as e:
        log.error(f"No se pudo listar los archivos en la carpeta (ID: {folder_id}): {str(e)}")



















def show_command_help(command):
    commands = {
        "cd": {
            "description": "Navega entre carpetas especificando la ruta de la carpeta.",
            "usage": "Uso: python main.py cd <ruta_carpeta>"
        },
        "dir": {
            "description": "Lista las carpetas en el directorio raíz.",
            "usage": "Uso: python main.py dir"
        },
        "ls": {
            "description": "Muestra los elementos dentro de una carpeta especificada.",
            "usage": "Uso: python main.py ls <ruta_carpeta>"
        },
        "find": {
            "description": "Busca un archivo o carpeta por su ID.",
            "usage": "Uso: python main.py find <id>"
        },
        "upload": {
            "description": "Sube un archivo a la carpeta especificada.",
            "usage": "Uso: python main.py upload <ruta_archivo> <nombre_carpeta>"
        },
        "delete": {
            "description": "Elimina un archivo o carpeta por su ID.",
            "usage": "Uso: python main.py delete <id>"
        },
        "help": {
            "description": "Muestra la lista de comandos disponibles o la ayuda de un comando específico.",
            "usage": "Uso: python main.py help [<comando>]"
        }
    }

    if command in commands:
        log.info(commands[command]["usage"])
        log.info("Descripción: " + commands[command]["description"])
    else:
        log.error("Comando desconocido.")