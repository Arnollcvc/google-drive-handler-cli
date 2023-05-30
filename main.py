import os
import sys

from modules.logger import Logger
from modules.drive import upload_file
from modules.utils import navigate_folders, list_folders, list_files_in_folder, search_file_by_id

SERVICE_ACCOUNT_FILE = "credentials.json"
DEFAULT_FOLDER_NAME = "default-from-desk"
MAIN_PATH = os.getcwd()

log = Logger()

def show_menu():
    log.info("Opciones:")
    log.info("1. Navegar entre carpetas")
    log.info("2. Listar carpetas")
    log.info("3. Listar archivos en una carpeta")
    log.info("4. Buscar archivo por ID")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.warn("Uso: python script.py <opción>")
        show_menu()
    else:
        option = int(sys.argv[1])

        if option == 1:
            if len(sys.argv) < 3:
                log.info("Uso: python script.py 1 <ruta_carpeta>")
            else:
                folder_path = sys.argv[2]
                navigate_folders(folder_path)
        elif option == 2:
            list_folders()
        elif option == 3:
            if len(sys.argv) < 3:
                log.warn("Uso: python script.py 3 <ruta_carpeta>")
            else:
                folder_path = sys.argv[2]
                list_files_in_folder(folder_path)
        elif option == 4:
            if len(sys.argv) < 3:
                log.warn("Uso: python script.py 4 <id_archivo>")
            else:
                file_id = sys.argv[2]
                search_file_by_id(file_id)
        elif option == 5:
            file_path = sys.argv[2]
            folder_name = sys.argv[3]
            upload_file(file_path, folder_name)
        else:
            log.error("Opción inválida.")