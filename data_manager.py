# data_manager.py

import hashlib
import json
import os
from config import USERS_DATA_FILE_FULL_PATH, PRODUCTS_DATA_FILE_FULL_PATH, DATA_PATH

# --- Estado del Usuario Actual (global a este módulo) ---
usuario_actual = {"nombre": None, "rol": None}
hora_inicio_sesion_actual = None

# --- Variables en memoria para almacenar los datos cargados ---
_usuarios_data = {}
_productos_data = {}

def _asegurar_directorio_datos():
    """Asegura que el directorio 'data' exista. Lo crea si no existe."""
    if not os.path.exists(DATA_PATH):
        try:
            os.makedirs(DATA_PATH, exist_ok=True)
            print(f"INFO (data_manager): Directorio de datos '{DATA_PATH}' creado.")
        except OSError as e:
            print(f"ADVERTENCIA (data_manager): No se pudo crear el directorio de datos '{DATA_PATH}': {e}")

def _cargar_usuarios():
    """Carga los datos de usuarios desde users.json."""
    global _usuarios_data
    _asegurar_directorio_datos() # Asegurar que el directorio exista antes de operar

    if not os.path.exists(USERS_DATA_FILE_FULL_PATH):
        print(f"ADVERTENCIA: Archivo de usuarios '{USERS_DATA_FILE_FULL_PATH}' no encontrado. Inicializando con datos vacíos.")
        _usuarios_data = {}
        _guardar_usuarios() # Crea el archivo con estructura básica si no existe
        return

    try:
        with open(USERS_DATA_FILE_FULL_PATH, 'r', encoding='utf-8') as f:
            _usuarios_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Error al decodificar JSON de usuarios desde '{USERS_DATA_FILE_FULL_PATH}': {e}. Inicializando datos vacíos.")
        _usuarios_data = {}
    except Exception as e:
        print(f"ERROR: No se pudieron cargar los datos de usuarios desde '{USERS_DATA_FILE_FULL_PATH}': {e}. Inicializando datos vacíos.")
        _usuarios_data = {}

def _guardar_usuarios():
    """Guarda los datos de usuarios en users.json."""
    _asegurar_directorio_datos() # Asegurar que el directorio exista antes de operar
    try:
        with open(USERS_DATA_FILE_FULL_PATH, 'w', encoding='utf-8') as f:
            json.dump(_usuarios_data, f, indent=2, ensure_ascii=False)
        print(f"INFO (data_manager): Datos de usuarios guardados exitosamente en '{USERS_DATA_FILE_FULL_PATH}'.")
    except Exception as e:
        print(f"ERROR: No se pudieron guardar los datos de usuarios en '{USERS_DATA_FILE_FULL_PATH}': {e}")

def _cargar_productos():
    """Carga los datos de productos desde products.json."""
    global _productos_data
    _asegurar_directorio_datos() # Asegurar que el directorio exista antes de operar

    if not os.path.exists(PRODUCTS_DATA_FILE_FULL_PATH):
        print(f"ADVERTENCIA: Archivo de productos '{PRODUCTS_DATA_FILE_FULL_PATH}' no encontrado. Inicializando con datos vacíos.")
        _productos_data = {}
        _guardar_productos() # Crea el archivo con estructura básica si no existe
        return

    try:
        with open(PRODUCTS_DATA_FILE_FULL_PATH, 'r', encoding='utf-8') as f:
            _productos_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Error al decodificar JSON de productos desde '{PRODUCTS_DATA_FILE_FULL_PATH}': {e}. Inicializando datos vacíos.")
        _productos_data = {}
    except Exception as e:
        print(f"ERROR: No se pudieron cargar los datos de productos desde '{PRODUCTS_DATA_FILE_FULL_PATH}': {e}. Inicializando datos vacíos.")
        _productos_data = {}

def _guardar_productos():
    """Guarda los datos de productos en products.json."""
    _asegurar_directorio_datos() # Asegurar que el directorio exista antes de operar
    try:
        with open(PRODUCTS_DATA_FILE_FULL_PATH, 'w', encoding='utf-8') as f:
            json.dump(_productos_data, f, indent=2, ensure_ascii=False)
        print(f"INFO (data_manager): Datos de productos guardados exitosamente en '{PRODUCTS_DATA_FILE_FULL_PATH}'.")
    except Exception as e:
        print(f"ERROR: No se pudieron guardar los datos de productos en '{PRODUCTS_DATA_FILE_FULL_PATH}': {e}")

_cargar_usuarios()
_cargar_productos()

def get_productos_data():
    """Retorna una copia del diccionario de productos en memoria."""
    return _productos_data.copy()

def get_producto_data(nombre_producto):
    """Retorna los datos de un producto específico (como una copia), o None."""
    producto = _productos_data.get(nombre_producto)
    return producto.copy() if producto else None

def get_usuarios_registrados_data():
    """Retorna una copia del diccionario de usuarios en memoria."""
    return _usuarios_data.copy()

def actualizar_producto_data(nombre_producto, datos_actualizados):
    """Actualiza un producto existente en el diccionario en memoria y lo guarda en disco."""
    if nombre_producto in _productos_data:
        _productos_data[nombre_producto].update(datos_actualizados)
        _guardar_productos() # Guardar cambios en disco
        print(f"INFO (data_manager): Producto '{nombre_producto}' actualizado en memoria y disco.")
        return True
    print(f"ERROR (data_manager): Intento de actualizar producto no existente '{nombre_producto}'.")
    return False

def eliminar_producto_data(nombre_producto):
    """Elimina un producto del diccionario en memoria y lo guarda en disco."""
    if nombre_producto in _productos_data:
        del _productos_data[nombre_producto]
        _guardar_productos() # Guardar cambios en disco
        print(f"INFO (data_manager): Producto '{nombre_producto}' eliminado de memoria y disco.")
        return True
    print(f"ERROR (data_manager): Intento de eliminar producto no existente '{nombre_producto}'.")
    return False

def registrar_producto_data(nombre_producto, datos_producto):
    """Registra un nuevo producto en el diccionario en memoria y lo guarda en disco."""
    if nombre_producto not in _productos_data:
        _productos_data[nombre_producto] = datos_producto
        _guardar_productos() # Guardar cambios en disco
        print(f"INFO (data_manager): Producto '{nombre_producto}' registrado en memoria y disco.")
        return True
    print(f"ERROR (data_manager): Intento de registrar producto ya existente '{nombre_producto}'.")
    return False

# Funciones de Gestión de Usuarios (ahora guardan en users.json a través de _guardar_usuarios())
def actualizar_usuario_data(nombre_usuario, datos_actualizados):
    """Actualiza un usuario existente y guarda en disco."""
    if nombre_usuario in _usuarios_data:
        _usuarios_data[nombre_usuario].update(datos_actualizados)
        _guardar_usuarios()
        print(f"INFO (data_manager): Usuario '{nombre_usuario}' actualizado.")
        return True
    print(f"ERROR (data_manager): Intento de actualizar usuario no existente '{nombre_usuario}'.")
    return False

def registrar_usuario_data(nombre_usuario, datos_usuario):
    """Registra un nuevo usuario y guarda en disco."""
    if nombre_usuario not in _usuarios_data:
        _usuarios_data[nombre_usuario] = datos_usuario
        _guardar_usuarios()
        print(f"INFO (data_manager): Usuario '{nombre_usuario}' registrado.")
        return True
    print(f"ERROR (data_manager): Intento de registrar usuario ya existente '{nombre_usuario}'.")
    return False

def eliminar_usuario_data(nombre_usuario):
    """Elimina un usuario y guarda en disco."""
    if nombre_usuario in _usuarios_data:
        del _usuarios_data[nombre_usuario]
        _guardar_usuarios()
        print(f"INFO (data_manager): Usuario '{nombre_usuario}' eliminado.")
        return True
    print(f"ERROR (data_manager): Intento de eliminar usuario no existente '{nombre_usuario}'.")
    return False
