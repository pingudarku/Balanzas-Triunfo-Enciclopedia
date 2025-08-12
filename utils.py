# utils.py
# Funciones de utilidad general para la aplicación

import webbrowser
from tkinter import messagebox
from excel_logger import registrar_accion_excel # Importar para registrar la acción
import os
import pathlib  # NUEVO: Importado para manejar rutas de archivo de forma robusta
from config import MANUALES_PRODUCTOS_PATH # Importar la ruta de los manuales

def abrir_enlace_web_util(recurso, app_parent_for_messagebox=None):
    """
    Abre un recurso, que puede ser una URL web o un archivo PDF local.
    Registra la acción.
    app_parent_for_messagebox es la ventana raíz para los messageboxes.
    """
    registrar_accion_excel("Intento Abrir Recurso", f"Recurso: {recurso}") #
    
    if not recurso or not recurso.strip():
        messagebox.showinfo("Recurso no Disponible", "No hay un enlace o archivo válido para este recurso.", parent=app_parent_for_messagebox) #
        return

    recurso = recurso.strip()

    # Primero, verificar si es una URL web
    if recurso.startswith(('http://', 'https://')): #
        try:
            webbrowser.open(recurso, new=2) #
        except Exception as e:
            messagebox.showerror("Error al Abrir Enlace", f"No se pudo abrir el enlace: {recurso}\nError: {e}", parent=app_parent_for_messagebox) #
    
    # Si no es una URL, tratarlo como un archivo local
    else:
        # Construir la ruta completa al archivo del manual
        ruta_completa_recurso = os.path.join(MANUALES_PRODUCTOS_PATH, recurso)
        
        if os.path.exists(ruta_completa_recurso):
            try:
                # MODIFICADO: Se convierte la ruta a un formato URI (file://) para máxima compatibilidad.
                uri = pathlib.Path(ruta_completa_recurso).as_uri()
                webbrowser.open(uri)
            except Exception as e:
                messagebox.showerror("Error al Abrir Archivo", f"No se pudo abrir el archivo: {recurso}\nError: {e}", parent=app_parent_for_messagebox)
        else:
            messagebox.showwarning("Archivo no Encontrado", f"El archivo '{recurso}' no fue encontrado en la carpeta de manuales.", parent=app_parent_for_messagebox)