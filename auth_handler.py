# auth_handler.py
# Lógica para la autenticación y gestión de usuarios (simplificado: hashing directo sin salt).

import hashlib
# Ya no necesitamos 'secrets' ni 'string' si no usamos salt.
# Importa las funciones de gestión de datos de usuarios
from data_manager import get_usuarios_registrados_data, actualizar_usuario_data, registrar_usuario_data, eliminar_usuario_data

def _generar_hash_contrasena(contrasena_texto_plano):
    """
    Genera el hash SHA256 de una contraseña en texto plano.
    Este método NO usa salting, lo cual es menos seguro.
    Retorna solo el hash.
    """
    return hashlib.sha256(contrasena_texto_plano.encode()).hexdigest()

def _verificar_contrasena_hash(contrasena_guardada_hash, contrasena_ingresada):
    """
    Verifica una contraseña ingresada contra un hash guardado.
    Este método NO usa salting.
    Retorna True si la contraseña es correcta, False en caso contrario.
    """
    contrasena_ingresada_hash = _generar_hash_contrasena(contrasena_ingresada)
    return contrasena_guardada_hash == contrasena_ingresada_hash

def autenticar_usuario(nombre_usuario_ingresado, contrasena_ingresada):
    """
    Autentica un usuario.
    Retorna un diccionario con {'nombre': nombre, 'rol': rol} si la autenticación es exitosa,
    sino None.
    """
    usuarios = get_usuarios_registrados_data() # Obtiene los usuarios del data_manager
    if nombre_usuario_ingresado in usuarios:
        datos_usuario_guardados = usuarios[nombre_usuario_ingresado]
        contrasena_hash_guardada = datos_usuario_guardados.get("contrasena_hash")

        # Verifica que el usuario tenga un hash guardado
        if contrasena_hash_guardada:
            if _verificar_contrasena_hash(contrasena_hash_guardada, contrasena_ingresada):
                return {"nombre": nombre_usuario_ingresado, "rol": datos_usuario_guardados["rol"]}
            else:
                # Opcional: print para depuración
                print(f"DEBUG: Contraseña incorrecta para {nombre_usuario_ingresado}")
        else:
            print(f"ADVERTENCIA: Usuario '{nombre_usuario_ingresado}' no tiene hash de contraseña guardado.")
    return None

# --- Funciones de Administración de Usuarios (Ajustadas para no usar salt) ---

def cambiar_contrasena_usuario(nombre_usuario, nueva_contrasena):
    """
    Cambia la contraseña de un usuario.
    Genera el hash de la nueva contraseña sin salt.
    """
    hash_nuevo = _generar_hash_contrasena(nueva_contrasena)
    # Actualiza los datos del usuario en el data_manager. Elimina el 'salt' si existía.
    return actualizar_usuario_data(nombre_usuario, {"contrasena_hash": hash_nuevo, "salt": None}) # Poner salt a None

def cambiar_rol_usuario(nombre_usuario, nuevo_rol):
    """
    Cambia el rol de un usuario.
    """
    return actualizar_usuario_data(nombre_usuario, {"rol": nuevo_rol})

def registrar_nuevo_usuario(nombre_usuario, contrasena, rol):
    """
    Registra un nuevo usuario en el sistema.
    Retorna True si el registro es exitoso, False si el usuario ya existe o hay un error.
    """
    if nombre_usuario in get_usuarios_registrados_data():
        print(f"ERROR: Intento de registrar usuario ya existente '{nombre_usuario}'.")
        return False
    
    hash_nuevo = _generar_hash_contrasena(contrasena)
    
    datos_nuevo_usuario = {
        "contrasena_hash": hash_nuevo,
        "rol": rol,
        "salt": None # Asegurarse de que no haya salt para nuevos usuarios
    }
    return registrar_usuario_data(nombre_usuario, datos_nuevo_usuario)

def eliminar_usuario(nombre_usuario):
    """
    Elimina un usuario del sistema.
    """
    return eliminar_usuario_data(nombre_usuario)
