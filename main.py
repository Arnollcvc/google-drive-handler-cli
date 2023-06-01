import os
import sys

from modules.logger import Logger
from modules.drive import upload_file, delete_item_by_id
from modules.utils import navigate_folders, list_folders, list_files_in_folder, search_item_by_id, lfiles_in_folder, get_folder_item_count, show_command_help

DEFAULT_FOLDER_NAME = "default-from-desk"
MAIN_PATH = os.getcwd()

log = Logger()

def show_menu():
    log.info("""Opciones:
    \033[95mcd\033[0m      -Navegar entre carpetas.
    \033[95mdir\033[0m     -Listar carpetas en el directorio root.
    \033[95mls\033[0m      -Ver elementos dentro de una carpeta.
    \033[92mfind\033[0m    -Buscar archivo/carpetapor ID.
    \033[93mupload\033[0m  -Subir archivo a una carpeta.
    \033[91mdelete\033[0m  -Eliminar archivo/carpeta por ID.
    \033[92mhelp\033[0m    -Mostrar ayuda.
    """)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        log.warn("Uso: python main.py <opción> [argumentos]")
        show_menu()
    else:
        option = str(sys.argv[1])
        if option == "test":
            # print(get_folder_item_count(sys.argv[2]))
            lfiles_in_folder(sys.argv[2] if len(sys.argv) > 2 else "1pove-ITySL3uK1W5lMpzvsxN2kwR9gIV")
        elif option == "cd":
            if len(sys.argv) < 3:
                log.info("Uso: python main.py cd <ruta_carpeta>")
            else:
                folder_path = sys.argv[2]
                navigate_folders(folder_path)
        elif option == "dir":
            list_folders()
        elif option == "ls":
            if len(sys.argv) < 3:
                log.warn("Uso: python main.py ls <ruta_carpeta>")
            else:
                folder_path = sys.argv[2]
                list_files_in_folder(folder_path)
        elif option == "find":
            if len(sys.argv) < 3:
                log.warn("Uso: python main.py find <id>")
            else:
                file_id = sys.argv[2]
                search_item_by_id(file_id)
        elif option == "upload":
            if len(sys.argv) < 4:
                log.warn("Uso: python main.py upload <ruta_archivo> <nombre_carpeta>")
            else:
                file_path = sys.argv[2]
                folder_name = sys.argv[3]
                upload_file(file_path, folder_name)
        elif option == "delete":
            if len(sys.argv) < 3:
                log.warn("Uso: python main.py delete <id>")
            else:
                file_id = sys.argv[2]
                delete_item_by_id(file_id)
        elif option == "help":
            if len(sys.argv) < 3:
                show_menu()
            else:
                command = sys.argv[2]
                show_command_help(command)
        else:
            log.error("Opción inválida.")
#ID CARPETA = 1pove-ITySL3uK1W5lMpzvsxN2kwR9gIV