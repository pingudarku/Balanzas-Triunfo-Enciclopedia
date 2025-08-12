# config.py

import os

# --- Paleta de Colores ---
COLOR_HEADER_BG = "#0A234D"
COLOR_ERROR_TEXT = "#D8000C"
COLOR_HEADER_FG = "white"
COLOR_ACCENT = "#F39C12"
COLOR_BACKGROUND = "white"
COLOR_TEXT_GENERAL = "#333333"
COLOR_TEXT_ON_ACCENT = "white"
COLOR_LISTBOX_BG = "white"
COLOR_LISTBOX_FG = COLOR_TEXT_GENERAL
COLOR_LISTBOX_SELECT_BG = COLOR_ACCENT
COLOR_LISTBOX_SELECT_FG = COLOR_TEXT_ON_ACCENT
COLOR_TAB_INACTIVE_BG = "#E0E0E0"
COLOR_TAB_ACTIVE_BG = COLOR_HEADER_BG
COLOR_TAB_ACTIVE_FG = COLOR_HEADER_FG
COLOR_TAB_INACTIVE_FG = COLOR_TEXT_GENERAL
COLOR_ERROR_TEXT = "#D8000C"
# --- Rutas y Nombres de Archivo ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorio para las imágenes de los productos
IMAGENES_PRODUCTOS_DIR_NAME = "imagenes_productos"
IMAGENES_PRODUCTOS_PATH = os.path.join(BASE_DIR, IMAGENES_PRODUCTOS_DIR_NAME)

# Directorio para los manuales de los productos (PDFs locales)
MANUALES_PRODUCTOS_DIR_NAME = "manuales_productos"
MANUALES_PRODUCTOS_PATH = os.path.join(BASE_DIR, MANUALES_PRODUCTOS_DIR_NAME)

# Archivo de log de Excel
EXCEL_LOG_FILENAME = "registro_actividad_balanzas.xlsx"
LOGS_DIR_NAME = "logs"
LOGS_PATH = os.path.join(BASE_DIR, LOGS_DIR_NAME)
EXCEL_LOG_FILE_FULL_PATH = os.path.join(LOGS_PATH, EXCEL_LOG_FILENAME)

DATA_FOLDER_NAME = "data"
DATA_PATH = os.path.join(BASE_DIR, DATA_FOLDER_NAME)

USERS_DATA_FILENAME = "users.json"
PRODUCTS_DATA_FILENAME = "products.json"
USERS_DATA_FILE_FULL_PATH = os.path.join(DATA_PATH, USERS_DATA_FILENAME)
PRODUCTS_DATA_FILE_FULL_PATH = os.path.join(DATA_PATH, PRODUCTS_DATA_FILENAME)

# NUEVO: Directorio y ruta para el ícono de la aplicación
LOGO_APP_DIR_NAME = "logo_app_jr" # Nombre de la nueva carpeta propuesta
LOGO_APP_PATH = os.path.join(BASE_DIR, LOGO_APP_DIR_NAME)
LOGO_ICON_FILENAME = "logo.ico" # Nombre del archivo del ícono
LOGO_ICON_FULL_PATH = os.path.join(LOGO_APP_PATH, LOGO_ICON_FILENAME)
