# main_app.py
# Punto de entrada principal de la aplicación Balanzas Triunfo Enciclopedia.

import tkinter as tk
from config import COLOR_BACKGROUND, LOGO_ICON_FULL_PATH # Importar la nueva ruta del logo
from excel_logger import inicializar_excel_log
from ui_components import crear_ventana_login_ui, inicializar_enciclopedia_ui
import os # Necesario para verificar si el archivo de logo existe

if __name__ == "__main__":
    # 1. Inicializar el logger de Excel al arrancar la aplicación
    inicializar_excel_log()

    # 2. Crear la ventana principal (raíz) de la aplicación Tkinter
    root_app = tk.Tk()
    root_app.geometry("900x700") # Tamaño inicial, ajustado para más contenido
    root_app.configure(background=COLOR_BACKGROUND)
    root_app.minsize(800, 600) # Tamaño mínimo permitido (ventana)
    root_app.withdraw()
    
    # Intentar establecer el ícono de la aplicación usando la ruta definida en config.py
    if os.path.exists(LOGO_ICON_FULL_PATH):
        try:
            root_app.iconbitmap(LOGO_ICON_FULL_PATH)
        except tk.TclError as e:
            print(f"ADVERTENCIA: No se pudo cargar el ícono de la aplicación '{LOGO_ICON_FULL_PATH}': {e}")
            # Puedes considerar mostrar un messagebox aquí si el ícono es crítico,
            # pero una advertencia en consola es suficiente para un ícono..
    else:
        print(f"ADVERTENCIA: Archivo de ícono '{LOGO_ICON_FULL_PATH}' no encontrado.")

    # 3. Iniciar con la ventana de login.

    crear_ventana_login_ui(root_app, inicializar_enciclopedia_ui)

    # 4. Iniciar el bucle principal de Tkinter para que la aplicación corra y maneje eventos.
    root_app.mainloop()
