import os
import io
import sys

from googleapiclient.http import MediaIoBaseUpload

from modules.logger import Logger
import modules.utils as utils



log = Logger()
drive_service = utils.authenticate()

DEFAULT_FOLDER_NAME = "default-from-desk"
MAIN_PATH = os.getcwd()

def upload_file(file_path, folder_name):
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
        media = MediaIoBaseUpload(io.FileIO(file_path, 'rb'), mimetype=f"{utils.get_file_mimetype(file_path)}", chunksize=1024*1024, resumable=True)
        log.warn(f"Subiendo el archivo {os.path.basename(file_path)} a la carpeta '{folder_name}'...")
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        log.log(f"Archivo subido con exito!! (ID: {file.get('id')})")
    except FileNotFoundError:
        log.error(f"Archivo no encontrado: {file_path}")
        sys.exit(1)

def delete_item_by_id(item_id):
    try:
        item = utils.find_by_id(item_id)
        if not item:
            log.error(f"No se encontrón elementos con el ID: {item_id}")
            sys.exit(1)
        else:
            seguroxd = input(f"\033[91m[¿?]\033[0m ¿Seguro que desea eliminar '{item['name']}' (ID: {item_id})? (y/n): ")
            if seguroxd.lower() == 'y':
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    log.warn(f"Eliminando carpeta '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Carpeta eliminada correctamente.")
                    return
                elif item['mimeType'] == 'application/vnd.google-apps.document':
                    log.warn(f"Eliminando documento '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Documento eliminado correctamente.")
                    return
                elif item['mimeType'] == 'video/mp4':
                    log.warn(f"Eliminando video '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Video eliminado correctamente.")
                    return
                elif item['mimeType'] == 'audio/mp3':
                    log.warn(f"Eliminando audio '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Audio eliminado correctamente.")
                    return
                #png
                elif item['mimeType'] == 'image/png':
                    log.warn(f"Eliminando imagen '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Imagen eliminado correctamente.")
                    return
                #jpg
                elif item['mimeType'] == 'image/jpeg':
                    log.warn(f"Eliminando imagen '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Imagen eliminado correctamente.")
                    return
                else:
                    log.warn(f"Eliminando elemento '{item['name']}' | ID '{item_id}'")
                    drive_service.files().delete(fileId=item_id).execute()
                    log.log(f"Elemento eliminado correctamente.")
                    return
            elif seguroxd.lower() == 'n':
                log.warn("Operación cancelada.")
                return
    except Exception as e:
        log.error(f"No se pudo eliminar el elemento con ID '{item_id}': {str(e)}")
