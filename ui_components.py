# ui_components.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import os
import datetime
import re 

# Importaciones de otros módulos del proyecto
import config
import data_manager
import auth_handler 
from excel_logger import registrar_accion_excel
from utils import abrir_enlace_web_util

# -w- Variables de Módulo para Referencias a Widgets -w-
app_principal_ref = None # Referencia a la ventana Tkinter principal (root_app)
entrada_modelo_busqueda_widget = None
lista_sugerencias_busqueda_widget = None
notebook_widget = None
tab_info_producto_widget = None
frame_info_producto_dinamico = None
lbl_total_stock_widget = None
style_aplicacion_global = None

# Variable para almacenar la referencia a la ventana de login Toplevel
# Esto nos permite gestionarla más directamente.
ventana_login_actual_ref = None 

# --- Funciones Auxiliares de UI ---
def _limpiar_frame_contenido_widgets(frame):
    """Destruye todos los widgets dentro de un frame."""
    for widget in frame.winfo_children():
        widget.destroy()

def actualizar_sugerencias_ui(event=None):
    """Actualiza la lista de sugerencias de productos en la UI."""
    if entrada_modelo_busqueda_widget and lista_sugerencias_busqueda_widget:
        texto_busqueda = entrada_modelo_busqueda_widget.get().strip().lower()
        lista_sugerencias_busqueda_widget.delete(0, tk.END)
        productos_dict = data_manager.get_productos_data()
        if texto_busqueda:
            sugerencias = [p for p in productos_dict.keys() if p.lower().startswith(texto_busqueda)]
        else:
            sugerencias = sorted(productos_dict.keys())
        for s in sugerencias: lista_sugerencias_busqueda_widget.insert(tk.END, s)

def _calcular_y_actualizar_total_stock_ui():
    """Calcula y actualiza el stock total de productos en la UI (solo para administradores)."""
    if lbl_total_stock_widget and data_manager.usuario_actual["rol"] == "administrador":
        total = sum(int(d.get("stock", 0)) for d in data_manager.get_productos_data().values())
        lbl_total_stock_widget.config(text=f"Stock Total Global: {total} unidades")

def _es_url_valida(url_string):
    """Valida si un string es una URL HTTP/HTTPS básica o una ruta de archivo local existente.
    
    Args:
        url_string (str): La cadena a validar.

    Returns:
        bool: True si es una URL válida o una ruta de archivo local existente, False en caso contrario.
    """
    # Permitir cadenas vacías, ya que la ausencia de un recurso es válida.
    if not url_string: 
        return True
    
    # Comprobar si es una URL web (http o https)
    url_pattern = re.compile(r'^(http|https)://[^\s/$.?#].[^\s]*$')
    if re.match(url_pattern, url_string) is not None:
        return True
    
    # Si no es una URL web, comprobar si es una ruta de archivo local
    # Se asume que los manuales locales están dentro de MANUALES_PRODUCTOS_PATH
    ruta_completa_recurso = os.path.join(config.MANUALES_PRODUCTOS_PATH, url_string)
    if os.path.exists(ruta_completa_recurso):
        return True

    return False


# --- Funciones de Gestión de Sesión ---
def cerrar_sesion_ui():
    """Cierra la sesión actual, registra la acción y regresa a la ventana de login."""
    # Registra la duración de la sesión antes de limpiar los datos del usuario
    if data_manager.usuario_actual["nombre"]:
        duracion = datetime.datetime.now() - data_manager.hora_inicio_sesion_actual
        duracion_minutos = duracion.total_seconds() / 60
        registrar_accion_excel("Cierre Sesion", f"Usuario: {data_manager.usuario_actual['nombre']}", duracion_min=duracion_minutos)
    
    # Limpia los datos del usuario actual
    data_manager.usuario_actual = {"nombre": None, "rol": None}
    data_manager.hora_inicio_sesion_actual = None
    
    # Esconde la ventana principal (root_app)
    if app_principal_ref:
        app_principal_ref.withdraw()
        # Destruye todos los widgets que estaban en la ventana principal de la enciclopedia
        _limpiar_frame_contenido_widgets(app_principal_ref)
        
        # Vuelve a crear la ventana de login. 
        # La ventana principal (root_app) ya está oculta,
        # y la ventana de login se creará como un Toplevel sobre ella.
        crear_ventana_login_ui(app_principal_ref, inicializar_enciclopedia_ui)

# --- Funciones CRUD de Productos (con interacción UI) ---

def _abrir_ventana_registrar_producto_ui_accion():
    """Abre una ventana para registrar un nuevo producto."""
    ventana_reg = tk.Toplevel(app_principal_ref)
    ventana_reg.title("Registrar Nuevo Producto")
    ventana_reg.geometry("500x600")
    ventana_reg.configure(background=config.COLOR_BACKGROUND)
    ventana_reg.grab_set() 

    reg_style = ttk.Style(ventana_reg)
    reg_style.theme_use(style_aplicacion_global.theme_use())
    reg_style.configure("Reg.TFrame", background=config.COLOR_BACKGROUND)
    reg_style.configure("Reg.TLabel", background=config.COLOR_BACKGROUND, font=("Arial", 10))
    reg_style.configure("Reg.TEntry", font=("Arial", 10), padding=3)

    main_frame_reg = ttk.Frame(ventana_reg, style="Reg.TFrame", padding=15)
    main_frame_reg.pack(expand=True, fill="both")
    ttk.Label(main_frame_reg, text="Registrar Nuevo Producto", font=("Arial", 14, "bold"), background=config.COLOR_BACKGROUND, foreground=config.COLOR_HEADER_BG).pack(pady=(0,15))
    
    campos_reg_defs_ui = ["Nombre Producto:", "Serie:", "Manual (URL/Archivo):", "Calibración (URL):", "Batería:", "Info Adicional:", "Imagen (ej: nombre.png):", "Stock Inicial:"]
    entries_reg_ui = {}
    for campo_text_ui in campos_reg_defs_ui:
        row_frame_ui = ttk.Frame(main_frame_reg, style="Reg.TFrame")
        row_frame_ui.pack(fill="x", pady=3)
        ttk.Label(row_frame_ui, text=campo_text_ui, style="Reg.TLabel", width=20).pack(side="left")
        # Se actualiza el reemplazo para el texto del campo 'Manual' para que coincida con '(URL/Archivo)'
        key_reg_ui = campo_text_ui.split(":")[0].lower().replace(" (url)", "").replace(" (url/archivo)", "").replace(" (ej nombrepng)", "").replace(" ", "_")
        if campo_text_ui == "Info Adicional:": entry_ui = tk.Text(row_frame_ui, font=("Arial", 10), width=35, height=4, relief="solid", borderwidth=1, wrap="word")
        else: entry_ui = ttk.Entry(row_frame_ui, style="Reg.TEntry", width=35)
        entry_ui.pack(side="left", fill="x", expand=True)
        entries_reg_ui[key_reg_ui] = entry_ui
    
    def guardar_nuevo_prod_accion_interna():
        nuevo_nombre_prod = entries_reg_ui["nombre_producto"].get().strip()
        if not nuevo_nombre_prod: 
            messagebox.showerror("Error", "El nombre del producto es obligatorio.", parent=ventana_reg)
            return
        
        if nuevo_nombre_prod in data_manager.get_productos_data(): 
            messagebox.showerror("Error", f"El producto '{nuevo_nombre_prod}' ya existe.", parent=ventana_reg)
            return
        
        try:
            stock_str_reg_ui = entries_reg_ui["stock_inicial"].get().strip()
            if not stock_str_reg_ui.isdigit() or int(stock_str_reg_ui) < 0: 
                messagebox.showerror("Error", "El stock debe ser un número entero mayor o igual a 0.", parent=ventana_reg)
                return
            
            manual_url = entries_reg_ui["manual"].get().strip()
            calibracion_url = entries_reg_ui["calibracion"].get().strip()

            # La validación ahora permite URLs o nombres de archivo locales
            if manual_url and not _es_url_valida(manual_url):
                messagebox.showerror("Error de Validación", "URL/Archivo del manual no válida. Debe comenzar con http:// o https://, o ser un nombre de archivo local existente en la carpeta de manuales.", parent=ventana_reg)
                return
            if calibracion_url and not _es_url_valida(calibracion_url):
                messagebox.showerror("Error de Validación", "URL de calibración no válida. Debe comenzar con http:// o https://.", parent=ventana_reg)
                return

            nuevo_producto_datos_reg = {
                "serie": entries_reg_ui["serie"].get().strip(),
                "manual": manual_url,
                "calibracion": calibracion_url,
                "bateria": entries_reg_ui["bateria"].get().strip(),
                "info": entries_reg_ui["info_adicional"].get("1.0", tk.END).strip(),
                "imagen": entries_reg_ui["imagen"].get().strip(),
                "stock": int(stock_str_reg_ui)
            }
            
            if data_manager.registrar_producto_data(nuevo_nombre_prod, nuevo_producto_datos_reg):
                registrar_accion_excel("Registro Producto", f"Producto: {nuevo_nombre_prod}, Stock: {nuevo_producto_datos_reg['stock']}")
                messagebox.showinfo("Éxito", f"Producto '{nuevo_nombre_prod}' registrado.", parent=ventana_reg)
                actualizar_sugerencias_ui()
                _calcular_y_actualizar_total_stock_ui()
                ventana_reg.destroy() 
            else: messagebox.showerror("Error", f"No se pudo registrar '{nuevo_nombre_prod}'.", parent=ventana_reg)
        except Exception as e: messagebox.showerror("Error al Guardar", str(e), parent=ventana_reg)

    ttk.Button(main_frame_reg, text="Guardar Producto", command=guardar_nuevo_prod_accion_interna, style="Accent.TButton").pack(pady=20)
    entries_reg_ui["nombre_producto"].focus()


def _abrir_ventana_editar_producto_ui_accion(nombre_producto_original):
    """Abre una ventana para editar un producto existente."""
    if data_manager.usuario_actual["rol"] != "administrador":
        messagebox.showwarning("Acceso Denegado", "Solo administradores pueden editar productos.", parent=app_principal_ref)
        return

    datos_prod = data_manager.get_producto_data(nombre_producto_original)
    if not datos_prod:
        messagebox.showerror("Error", f"Producto '{nombre_producto_original}' no encontrado para editar.", parent=app_principal_ref)
        return

    ventana_editar = tk.Toplevel(app_principal_ref)
    ventana_editar.title(f"Editar Producto: {nombre_producto_original}")
    ventana_editar.geometry("500x650")
    ventana_editar.configure(background=config.COLOR_BACKGROUND)
    ventana_editar.grab_set()

    edit_style = ttk.Style(ventana_editar)
    edit_style.theme_use(style_aplicacion_global.theme_use())
    edit_style.configure("Edit.TFrame", background=config.COLOR_BACKGROUND)
    edit_style.configure("Edit.TLabel", background=config.COLOR_BACKGROUND, font=("Arial", 10))
    edit_style.configure("Edit.TEntry", font=("Arial", 10), padding=3)

    main_frame_edit = ttk.Frame(ventana_editar, style="Edit.TFrame", padding=15)
    main_frame_edit.pack(expand=True, fill="both")
    ttk.Label(main_frame_edit, text=f"Editar Producto: {nombre_producto_original}", font=("Arial", 14, "bold"), background=config.COLOR_BACKGROUND, foreground=config.COLOR_HEADER_BG).pack(pady=(0,15))

    campos_edit_defs_ui = ["Nombre Producto:", "Serie:", "Manual (URL/Archivo):", "Calibración (URL):", "Batería:", "Info Adicional:", "Imagen (ej: nombre.png):", "Stock:"]
    entries_edit_ui = {}
    for campo_text_ui in campos_edit_defs_ui:
        row_frame_ui = ttk.Frame(main_frame_edit, style="Edit.TFrame")
        row_frame_ui.pack(fill="x", pady=3)
        ttk.Label(row_frame_ui, text=campo_text_ui, style="Edit.TLabel", width=20).pack(side="left")
        key_edit_ui = campo_text_ui.split(":")[0].lower().replace(" (url)", "").replace(" (url/archivo)", "").replace(" (ej nombrepng)", "").replace(" ", "_")
        
        if key_edit_ui == "nombre_producto":
            entry_ui = ttk.Label(row_frame_ui, text=nombre_producto_original, style="Edit.TLabel")
            entry_ui.pack(side="left", fill="x", expand=True)
        elif campo_text_ui == "Info Adicional:": 
            entry_ui = tk.Text(row_frame_ui, font=("Arial", 10), width=35, height=4, relief="solid", borderwidth=1, wrap="word")
            entry_ui.insert("1.0", datos_prod.get("info", ""))
            entry_ui.pack(side="left", fill="x", expand=True)
            entries_edit_ui["info"] = entry_ui
        else: 
            entry_ui = ttk.Entry(row_frame_ui, style="Edit.TEntry", width=35)
            entry_ui.insert(0, datos_prod.get(key_edit_ui, ''))
            entry_ui.pack(side="left", fill="x", expand=True)
            entries_edit_ui[key_edit_ui] = entry_ui
    
    def _guardar_cambios_prod_accion_interna():
        try:
            datos_para_actualizar = {}
            cambios_detectados_log = []
            
            for key, entry_widget in entries_edit_ui.items():
                valor_actual_en_db = str(datos_prod.get(key, ''))
                valor_nuevo_del_widget = entry_widget.get("1.0", tk.END).strip() if isinstance(entry_widget, tk.Text) else entry_widget.get().strip()
                
                if key == "stock":
                    if not valor_nuevo_del_widget.isdigit() or int(valor_nuevo_del_widget) < 0:
                        messagebox.showerror("Error de Validación", "Stock debe ser un número entero mayor o igual a 0.", parent=ventana_editar)
                        return
                    valor_nuevo_parsed = int(valor_nuevo_del_widget)
                    if valor_nuevo_parsed != int(valor_actual_en_db if valor_actual_en_db.isdigit() else -1):
                        cambios_detectados_log.append(f"{key}: '{valor_actual_en_db}' -> '{valor_nuevo_parsed}'")
                    datos_para_actualizar[key] = valor_nuevo_parsed
                elif key in ["manual", "calibracion"]: 
                    if valor_nuevo_del_widget and not _es_url_valida(valor_nuevo_del_widget):
                        messagebox.showerror("Error de Validación", f"URL/Archivo de {key} no válida.", parent=ventana_editar)
                        return
                    if valor_nuevo_del_widget != valor_actual_en_db:
                        cambios_detectados_log.append(f"{key}: '{valor_actual_en_db}' -> '{valor_nuevo_del_widget}'")
                    datos_para_actualizar[key] = valor_nuevo_del_widget
                else:
                    if valor_nuevo_del_widget != valor_actual_en_db:
                        cambios_detectados_log.append(f"{key}: '{valor_actual_en_db}' -> '{valor_nuevo_del_widget}'")
                    datos_para_actualizar[key] = valor_nuevo_del_widget
            
            if not cambios_detectados_log:
                messagebox.showinfo("Sin Cambios", "No se detectaron cambios para guardar.", parent=ventana_editar); return

            if data_manager.actualizar_producto_data(nombre_producto_original, datos_para_actualizar):
                detalle_log = f"Producto: {nombre_producto_original}. Cambios: {'; '.join(cambios_detectados_log)}"
                registrar_accion_excel("Edicion Producto (Guardado)", detalle_log)
                messagebox.showinfo("Éxito", f"Producto '{nombre_producto_original}' actualizado.", parent=ventana_editar)
                _calcular_y_actualizar_total_stock_ui()
                mostrar_informacion_producto_seleccionado_ui() 
                ventana_editar.destroy()
            else:
                messagebox.showerror("Error", "No se pudo actualizar el producto en el gestor de datos.", parent=ventana_editar)

        except Exception as e: messagebox.showerror("Error", f"No se guardaron cambios: {e}", parent=ventana_editar)

    def _eliminar_producto_desde_edicion():
        if messagebox.askyesno("Confirmar Eliminación", f"¿Realmente desea eliminar el producto '{nombre_producto_original}'?", parent=ventana_editar):
            if data_manager.eliminar_producto_data(nombre_producto_original):
                registrar_accion_excel("Eliminacion Producto", f"Producto: {nombre_producto_original}")
                messagebox.showinfo("Éxito", f"Producto '{nombre_producto_original}' eliminado.", parent=ventana_editar)
                _limpiar_frame_contenido_widgets(frame_info_producto_dinamico) 
                ttk.Label(frame_info_producto_dinamico, text="Producto eliminado. Seleccione otro.", style="Info.TLabel", justify=tk.CENTER).pack(expand=True, padx=20, pady=20)
                actualizar_sugerencias_ui() 
                _calcular_y_actualizar_total_stock_ui()
                ventana_editar.destroy()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el producto del gestor de datos.", parent=ventana_editar)


    btn_frame_edit = ttk.Frame(main_frame_edit, style="Edit.TFrame")
    btn_frame_edit.pack(pady=20)
    ttk.Button(btn_frame_edit, text="Guardar Cambios", command=_guardar_cambios_prod_accion_interna, style="Accent.TButton").pack(side="left", padx=(0,10))
    ttk.Button(btn_frame_edit, text="Eliminar Producto", command=_eliminar_producto_desde_edicion, style="Accent.TButton").pack(side="left")

    if "serie" in entries_edit_ui:
        entries_edit_ui["serie"].focus()


# --- Lógica Principal de la UI de la Enciclopedia ---
def mostrar_informacion_producto_seleccionado_ui(event=None):
    """Muestra la información del producto seleccionado en la UI."""
    _limpiar_frame_contenido_widgets(frame_info_producto_dinamico) 
    
    if not lista_sugerencias_busqueda_widget: return
    indices = lista_sugerencias_busqueda_widget.curselection()
    if not indices:
        ttk.Label(frame_info_producto_dinamico, text="Seleccione un producto (doble clic) para ver su información.", style="Info.TLabel", justify=tk.CENTER).pack(expand=True, padx=20, pady=20)
        return
        
    nombre_sel = lista_sugerencias_busqueda_widget.get(indices[0])
    datos_prod = data_manager.get_producto_data(nombre_sel)

    registrar_accion_excel("Consulta Producto", f"Producto: {nombre_sel}")

    if not datos_prod: messagebox.showerror("Error", f"Datos no encontrados para {nombre_sel}.", parent=app_principal_ref); return
    if notebook_widget and tab_info_producto_widget: notebook_widget.select(tab_info_producto_widget)

    main_info_frame = ttk.Frame(frame_info_producto_dinamico, style="Content.TFrame")
    main_info_frame.pack(expand=True, fill="both", padx=10, pady=10)
    text_frame = ttk.Frame(main_info_frame, style="Content.TFrame")
    text_frame.pack(side="left", fill="both", expand=True, padx=(0,10))
    
    image_display_frame = ttk.Frame(main_info_frame, style="Content.TFrame", width=220, height=270)
    image_display_frame.pack(side="right", fill="none", expand=False, padx=(10,0), anchor="ne")
    image_display_frame.pack_propagate(False)

    img_filename = datos_prod.get('imagen', '')
    if img_filename:
        try:
            ruta_img = os.path.join(config.IMAGENES_PRODUCTOS_PATH, img_filename)
            if os.path.exists(ruta_img):
                img_original_pil = Image.open(ruta_img)
                img_original_pil.thumbnail((200, 250)) 
                img_tk_render_obj = ImageTk.PhotoImage(img_original_pil)
                lbl_img_widget = tk.Label(image_display_frame, image=img_tk_render_obj, bg=config.COLOR_BACKGROUND)
                lbl_img_widget.image = img_tk_render_obj
                lbl_img_widget.pack(pady=5, padx=5, anchor="center")
            else:
                error_msg = f"(Imagen '{img_filename}' no encontrada)"
                ttk.Label(image_display_frame, text=error_msg, style="ErrorImage.TLabel", wraplength=180).pack(pady=10, padx=5, anchor="n")
        except Exception as e:
            error_detalle = f"(Error al procesar imagen: {e})"
            ttk.Label(image_display_frame, text=error_detalle, style="ErrorImage.TLabel", wraplength=180).pack(pady=10, padx=5, anchor="n")
    else:
        ttk.Label(image_display_frame, text="(Sin imagen asignada)", style="Info.TLabel").pack(pady=10, padx=5, anchor="n")
    
    ttk.Label(text_frame, text=f"Producto: {nombre_sel}", style="Info.Header.TLabel").pack(pady=(0, 10), anchor="nw")
    
    campos_def = {"serie": "Número de serie:", "manual": "Manual:", "calibracion": "Calibración:", "bateria": "Batería:", "info": "Info Adicional:", "imagen": "Archivo Imagen:", "stock": "Stock:"}
    
    for key, label_txt in campos_def.items():
        # Los campos 'imagen' y 'stock' solo se muestran para administradores.
        # Los botones de acción se gestionan por separado más abajo, por lo que este bucle solo
        # se encarga de mostrar la etiqueta de texto y el valor del campo.
        if data_manager.usuario_actual["rol"] != 'administrador' and key in ['imagen', 'stock']:
            continue
            
        item_f = ttk.Frame(text_frame, style="Content.TFrame")
        item_f.pack(fill="x", pady=3, anchor="nw")
        ttk.Label(item_f, text=label_txt, style="Info.Bold.TLabel", width=18).pack(side="left", anchor="nw", padx=(0,5))
        
        val_dato = str(datos_prod.get(key, ''))

        texto_a_mostrar = val_dato.strip() if val_dato.strip() else "No disponible"
        
        # MODIFICADO: Lógica para mostrar "Disponible" o "No disponible"
        if key in ["manual", "calibracion"]:
            if val_dato.strip() and _es_url_valida(val_dato):
                texto_a_mostrar = "Disponible"
            else:
                texto_a_mostrar = "No disponible"

        if key == "info":
            lbl_val_w = ttk.Label(item_f, text=texto_a_mostrar, style="Info.TLabel", wraplength=text_frame.winfo_width() - 150 if text_frame.winfo_width() > 150 else 250)
            lbl_val_w.pack(side="left", anchor="nw")
        else:
            ttk.Label(item_f, text=texto_a_mostrar, style="Info.TLabel").pack(side="left", anchor="nw")

    btns_enlaces_f = ttk.Frame(text_frame, style="Content.TFrame")
    btns_enlaces_f.pack(fill="x", pady=(15,5), anchor="nw")
    
    manual_valor = datos_prod.get('manual', '').strip()
    # Se muestra el botón "Ver Manual" si hay un valor válido.
    if manual_valor and _es_url_valida(manual_valor): 
        ttk.Button(btns_enlaces_f, text="Ver Manual", style="Accent.TButton", command=lambda m=manual_valor: abrir_enlace_web_util(m, app_principal_ref)).pack(side="left", padx=(0,10))
    
    calibracion_valor = datos_prod.get('calibracion', '').strip()
    # Se muestra el botón "Ver Calibración" si hay un valor válido.
    if calibracion_valor and _es_url_valida(calibracion_valor): 
        ttk.Button(btns_enlaces_f, text="Ver Calibración", style="Accent.TButton", command=lambda c=calibracion_valor: abrir_enlace_web_util(c, app_principal_ref)).pack(side="left", padx=(0,10))

    if data_manager.usuario_actual["rol"] == "administrador":
        admin_acts_f = ttk.Frame(text_frame, style="Content.TFrame")
        admin_acts_f.pack(fill="x", pady=(10,5), anchor="nw", after=btns_enlaces_f)
        ttk.Button(admin_acts_f, text="Editar/Eliminar Producto", style="Accent.TButton", command=lambda np=nombre_sel: _abrir_ventana_editar_producto_ui_accion(np)).pack(side="left", padx=(0,10))

# --- Funciones para la Gestión de Usuarios ---
def _abrir_ventana_gestion_usuarios_ui_accion():
    """Abre una ventana para que el administrador gestione usuarios."""
    if data_manager.usuario_actual["rol"] != "administrador":
        messagebox.showwarning("Acceso Denegado", "Solo administradores pueden gestionar usuarios.", parent=app_principal_ref)
        return

    ventana_gestion_usuarios = tk.Toplevel(app_principal_ref)
    ventana_gestion_usuarios.title("Gestión de Usuarios")
    ventana_gestion_usuarios.geometry("600x500")
    ventana_gestion_usuarios.configure(background=config.COLOR_BACKGROUND)
    ventana_gestion_usuarios.grab_set() 

    gestion_style = ttk.Style(ventana_gestion_usuarios)
    gestion_style.theme_use(style_aplicacion_global.theme_use())
    gestion_style.configure("UserMgmt.TFrame", background=config.COLOR_BACKGROUND)
    gestion_style.configure("UserMgmt.TLabel", background=config.COLOR_BACKGROUND, font=("Arial", 10))
    gestion_style.configure("UserMgmt.TEntry", font=("Arial", 10), padding=3)

    main_frame_user_mgmt = ttk.Frame(ventana_gestion_usuarios, style="UserMgmt.TFrame", padding=15)
    main_frame_user_mgmt.pack(expand=True, fill="both")
    ttk.Label(main_frame_user_mgmt, text="Gestión de Usuarios", font=("Arial", 14, "bold"), background=config.COLOR_BACKGROUND, foreground=config.COLOR_HEADER_BG).pack(pady=(0,15))

    frame_lista_usuarios = ttk.Frame(main_frame_user_mgmt, style="UserMgmt.TFrame")
    frame_lista_usuarios.pack(fill="both", expand=True, pady=5)
    
    lbl_usuarios = ttk.Label(frame_lista_usuarios, text="Usuarios Existentes:", style="UserMgmt.TLabel")
    lbl_usuarios.pack(anchor="w")

    lista_usuarios_widget = tk.Listbox(frame_lista_usuarios, font=("Arial", 11), width=40, height=8, bg=config.COLOR_LISTBOX_BG, fg=config.COLOR_LISTBOX_FG, selectbackground=config.COLOR_LISTBOX_SELECT_BG, selectforeground=config.COLOR_LISTBOX_SELECT_FG, borderwidth=1, relief="solid", exportselection=False)
    lista_usuarios_widget.pack(side="left", fill="both", expand=True)
    scrollbar_usuarios = ttk.Scrollbar(frame_lista_usuarios, orient="vertical", command=lista_usuarios_widget.yview)
    scrollbar_usuarios.pack(side="right", fill="y")
    lista_usuarios_widget.config(yscrollcommand=scrollbar_usuarios.set)

    frame_edicion_usuario = ttk.Frame(main_frame_user_mgmt, style="UserMgmt.TFrame")
    frame_edicion_usuario.pack(fill="x", pady=10)

    ttk.Label(frame_edicion_usuario, text="Usuario Seleccionado:", style="UserMgmt.TLabel").pack(anchor="w")
    current_username_label = ttk.Label(frame_edicion_usuario, text="", style="Info.Bold.TLabel")
    current_username_label.pack(anchor="w", pady=(0,5))

    ttk.Label(frame_edicion_usuario, text="Nuevo Rol:", style="UserMgmt.TLabel").pack(anchor="w")
    combo_rol = ttk.Combobox(frame_edicion_usuario, values=["usuario", "administrador"], state="readonly", style="Reg.TEntry")
    combo_rol.pack(fill="x", pady=(0,5))

    ttk.Label(frame_edicion_usuario, text="Nueva Contraseña (dejar vacío para no cambiar):", style="UserMgmt.TLabel").pack(anchor="w")
    entry_nueva_contrasena = ttk.Entry(frame_edicion_usuario, show="*", style="Reg.TEntry")
    entry_nueva_contrasena.pack(fill="x", pady=(0,10))

    def _actualizar_lista_usuarios():
        """Carga la lista de usuarios desde data_manager y la muestra en la Listbox."""
        lista_usuarios_widget.delete(0, tk.END)
        for user_name in data_manager.get_usuarios_registrados_data().keys():
            lista_usuarios_widget.insert(tk.END, user_name)
        current_username_label.config(text="") 
        combo_rol.set("")
        entry_nueva_contrasena.set("")

    def _seleccionar_usuario_para_edicion(event=None):
        """Maneja la selección de un usuario en la Listbox para editarlo."""
        indices = lista_usuarios_widget.curselection()
        if not indices: return
        nombre_sel = lista_usuarios_widget.get(indices[0])
        current_username_label.config(text=nombre_sel)
        user_data = data_manager.get_usuarios_registrados_data().get(nombre_sel, {})
        combo_rol.set(user_data.get("rol", ""))
        entry_nueva_contrasena.set("") 

    def _guardar_cambios_usuario():
        """Guarda los cambios realizados en un usuario seleccionado."""
        nombre_usuario_sel = current_username_label.cget("text")
        if not nombre_usuario_sel:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para editar.", parent=ventana_gestion_usuarios)
            return

        nuevo_rol = combo_rol.get().strip()
        nueva_contrasena = entry_nueva_contrasena.get().strip()
        
        cambios_detectados = []
        usuario_actual_data = data_manager.get_usuarios_registrados_data().get(nombre_usuario_sel, {})

        if nuevo_rol and nuevo_rol != usuario_actual_data.get("rol"):
            if auth_handler.cambiar_rol_usuario(nombre_usuario_sel, nuevo_rol):
                cambios_detectados.append(f"Rol: '{usuario_actual_data.get('rol')}' -> '{nuevo_rol}'")
            else:
                messagebox.showerror("Error", f"No se pudo cambiar el rol para '{nombre_usuario_sel}'.", parent=ventana_gestion_usuarios)
                return

        if nueva_contrasena:
            if auth_handler.cambiar_contrasena_usuario(nombre_usuario_sel, nueva_contrasena):
                cambios_detectados.append(f"Contraseña cambiada.")
            else:
                messagebox.showerror("Error", f"No se pudo cambiar la contraseña para '{nombre_usuario_sel}'.", parent=ventana_gestion_usuarios)
                return

        if cambios_detectados:
            detalle_log = f"Usuario: {nombre_usuario_sel}. Cambios: {'; '.join(cambios_detectados)}"
            registrar_accion_excel("Edicion Usuario", detalle_log)
            messagebox.showinfo("Éxito", f"Usuario '{nombre_usuario_sel}' actualizado.", parent=ventana_gestion_usuarios)
            _actualizar_lista_usuarios() 
        else:
            messagebox.showinfo("Sin Cambios", "No se detectaron cambios para guardar.", parent=ventana_gestion_usuarios)

    def _registrar_nuevo_usuario_ui_accion():
        """Abre una ventana para registrar un nuevo usuario."""
        ventana_nuevo_usuario = tk.Toplevel(ventana_gestion_usuarios)
        ventana_nuevo_usuario.title("Registrar Nuevo Usuario")
        ventana_nuevo_usuario.geometry("350x250")
        ventana_nuevo_usuario.configure(background=config.COLOR_BACKGROUND)
        ventana_nuevo_usuario.grab_set()

        frame_nuevo = ttk.Frame(ventana_nuevo_usuario, style="Reg.TFrame", padding=15)
        frame_nuevo.pack(expand=True, fill="both")

        ttk.Label(frame_nuevo, text="Nombre de Usuario:", style="Reg.TLabel").pack(anchor="w")
        entry_nombre_nuevo = ttk.Entry(frame_nuevo, style="Reg.TEntry")
        entry_nombre_nuevo.pack(fill="x", pady=(0,5))

        ttk.Label(frame_nuevo, text="Contraseña:", style="Reg.TLabel").pack(anchor="w")
        entry_pass_nuevo = ttk.Entry(frame_nuevo, show="*", style="Reg.TEntry")
        entry_pass_nuevo.pack(fill="x", pady=(0,5))

        ttk.Label(frame_nuevo, text="Rol:", style="Reg.TLabel").pack(anchor="w")
        combo_rol_nuevo = ttk.Combobox(frame_nuevo, values=["usuario", "administrador"], state="readonly", style="Reg.TEntry")
        combo_rol_nuevo.pack(fill="x", pady=(0,10))
        combo_rol_nuevo.set("usuario")

        def _guardar_nuevo_usuario():
            """Guarda el nuevo usuario registrado."""
            nombre = entry_nombre_nuevo.get().strip()
            contrasena = entry_pass_nuevo.get().strip()
            rol = combo_rol_nuevo.get().strip()

            if not nombre or not contrasena or not rol:
                messagebox.showerror("Error", "Todos los campos son obligatorios para un nuevo usuario.", parent=ventana_nuevo_usuario)
                return
            
            if auth_handler.registrar_nuevo_usuario(nombre, contrasena, rol):
                registrar_accion_excel("Registro Usuario", f"Usuario: {nombre}, Rol: {rol}")
                messagebox.showinfo("Éxito", f"Usuario '{nombre}' registrado.", parent=ventana_nuevo_usuario)
                _actualizar_lista_usuarios()
                ventana_nuevo_usuario.destroy()
            else:
                messagebox.showerror("Error", f"El usuario '{nombre}' ya existe o hubo un error al registrar.", parent=ventana_nuevo_usuario)

        ttk.Button(frame_nuevo, text="Registrar", command=_guardar_nuevo_usuario, style="Accent.TButton").pack(pady=10)

    def _eliminar_usuario_ui_accion():
        """Elimina un usuario seleccionado."""
        nombre_usuario_sel = current_username_label.cget("text")
        if not nombre_usuario_sel:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar.", parent=ventana_gestion_usuarios)
            return
        
        if nombre_usuario_sel == data_manager.usuario_actual["nombre"]:
            messagebox.showerror("Error", "No puedes eliminar tu propio usuario mientras estás logueado.", parent=ventana_gestion_usuarios)
            return

        if messagebox.askyesno("Confirmar Eliminación", f"¿Realmente desea eliminar el usuario '{nombre_usuario_sel}'? Esta acción es irreversible.", parent=ventana_gestion_usuarios):
            if auth_handler.eliminar_usuario(nombre_usuario_sel):
                registrar_accion_excel("Eliminacion Usuario", f"Usuario: {nombre_usuario_sel}") # CORREGIDO: Usar nombre_usuario_sel
                messagebox.showinfo("Eliminado", f"Usuario '{nombre_usuario_sel}' eliminado.", parent=ventana_gestion_usuarios)
                _actualizar_lista_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo eliminar el usuario.", parent=ventana_gestion_usuarios)


    btn_frame_user_mgmt = ttk.Frame(main_frame_user_mgmt, style="UserMgmt.TFrame")
    btn_frame_user_mgmt.pack(fill="x", pady=10)

    # Botones de acción para la gestión de usuarios
    ttk.Button(btn_frame_user_mgmt, text="Guardar Cambios", command=_guardar_cambios_usuario, style="Accent.TButton").pack(side="left", padx=(0,10))
    ttk.Button(btn_frame_user_mgmt, text="Registrar Nuevo", command=_registrar_nuevo_usuario_ui_accion, style="Accent.TButton").pack(side="left", padx=(0,10))
    ttk.Button(btn_frame_user_mgmt, text="Eliminar Usuario", command=_eliminar_usuario_ui_accion, style="Accent.TButton").pack(side="left")

    lista_usuarios_widget.bind("<<ListboxSelect>>", _seleccionar_usuario_para_edicion)
    _actualizar_lista_usuarios()

# --- Funciones para Construir las Ventanas Principales ---
def _intentar_login_ui_logic(entry_usuario, entry_contrasena, ventana_login_ref_local, app_main_ref, callback_exito_login_ref):
    """Lógica para intentar autenticar al usuario."""
    global ventana_login_actual_ref
    usuario_ingresado_login = entry_usuario.get().strip()
    contrasena_ingresada_login = entry_contrasena.get().strip()
    info_usuario_autenticado = auth_handler.autenticar_usuario(usuario_ingresado_login, contrasena_ingresada_login)
    
    if info_usuario_autenticado:
        data_manager.usuario_actual.update(info_usuario_autenticado)
        data_manager.hora_inicio_sesion_actual = datetime.datetime.now()
        registrar_accion_excel("Inicio Sesion", f"Usuario: {data_manager.usuario_actual['nombre']}, Rol: {data_manager.usuario_actual['rol']}")
        
        ventana_login_ref_local.destroy()
        ventana_login_actual_ref = None
        
        app_main_ref.deiconify()
        callback_exito_login_ref(app_main_ref)
    else:
        messagebox.showerror("Error de Inicio de Sesión", "Usuario o contraseña incorrectos.", parent=ventana_login_ref_local)

def crear_ventana_login_ui(app_principal_arg, callback_exito_login_arg):
    """Crea y muestra la ventana de inicio de sesión."""
    global app_principal_ref, ventana_login_actual_ref
    app_principal_ref = app_principal_arg

    if ventana_login_actual_ref and ventana_login_actual_ref.winfo_exists():
        ventana_login_actual_ref.destroy()

    ventana_login_ui = tk.Toplevel(app_principal_ref)
    ventana_login_ui.title("Inicio de Sesión")
    # --- Modificar la resolución aquí ---
    ventana_login_ui.geometry("400x280") # Puedes cambiar "400x280" a la resolución deseada, por ejemplo, "600x400"
    # --- Fin de la modificación ---
    ventana_login_ui.resizable(False, False)
    ventana_login_ui.configure(background=config.COLOR_BACKGROUND)
    ventana_login_ui.grab_set()
    ventana_login_ui.protocol("WM_DELETE_WINDOW", lambda: on_app_close_ui())

    ventana_login_actual_ref = ventana_login_ui

    login_ui_style_local = ttk.Style(ventana_login_ui)
    try: login_ui_style_local.theme_use('clam')
    except tk.TclError: login_ui_style_local.theme_use('default')
    login_ui_style_local.configure("Login.TFrame", background=config.COLOR_BACKGROUND)
    login_ui_style_local.configure("Login.Header.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_HEADER_BG, font=("Arial", 16, "bold"))
    login_ui_style_local.configure("Login.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_TEXT_GENERAL, font=("Arial", 11))
    login_ui_style_local.configure("Login.TEntry", font=("Arial", 11), padding=5)
    login_ui_style_local.configure("Login.TButton", font=("Arial", 11, "bold"), background=config.COLOR_ACCENT, foreground=config.COLOR_TEXT_ON_ACCENT, padding=(10,5))
    login_ui_style_local.map("Login.TButton", background=[('active', '#E88B0A')])
    
    login_main_frame = ttk.Frame(ventana_login_ui, style="Login.TFrame", padding=20)
    login_main_frame.pack(expand=True, fill="both")
    ttk.Label(login_main_frame, text="Acceso Enciclopedia", style="Login.Header.TLabel").pack(pady=(0, 20))
    ttk.Label(login_main_frame, text="Usuario:", style="Login.TLabel").pack(anchor="w", padx=10)
    entry_usuario_widget = ttk.Entry(login_main_frame, style="Login.TEntry", width=30)
    entry_usuario_widget.pack(pady=(0, 10), padx=10, fill="x")
    ttk.Label(login_main_frame, text="Contraseña:", style="Login.TLabel").pack(anchor="w", padx=10)
    entry_contrasena_widget = ttk.Entry(login_main_frame, style="Login.TEntry", show="*", width=30)
    entry_contrasena_widget.pack(pady=(0, 20), padx=10, fill="x")
    
    btn_ingresar_widget = ttk.Button(login_main_frame, text="Ingresar", style="Login.TButton", 
                            command=lambda: _intentar_login_ui_logic(entry_usuario_widget, entry_contrasena_widget, ventana_login_ui, app_principal_ref, callback_exito_login_arg))
    btn_ingresar_widget.pack(pady=10)
    
    ventana_login_ui.update_idletasks()
    x_pos_login = (ventana_login_ui.winfo_screenwidth() // 2) - (ventana_login_ui.winfo_width() // 2)
    y_pos_login = (ventana_login_ui.winfo_screenheight() // 2) - (ventana_login_ui.winfo_height() // 2)
    ventana_login_ui.geometry(f'+{x_pos_login}+{y_pos_login}')
    entry_usuario_widget.focus()

def inicializar_enciclopedia_ui(app_principal_arg):
    """Inicializa la interfaz principal de la enciclopedia después de un login exitoso."""
    global app_principal_ref, entrada_modelo_busqueda_widget, lista_sugerencias_busqueda_widget, notebook_widget, tab_info_producto_widget, frame_info_producto_dinamico, lbl_total_stock_widget, style_aplicacion_global

    app_principal_ref = app_principal_arg
    app_principal_ref.title(f"Balanzas Triunfo Enciclopedia - {data_manager.usuario_actual['nombre']} ({data_manager.usuario_actual['rol']})")
    app_principal_ref.protocol("WM_DELETE_WINDOW", on_app_close_ui)

    style_aplicacion_global = ttk.Style(app_principal_ref)
    try: style_aplicacion_global.theme_use('clam')
    except tk.TclError: style_aplicacion_global.theme_use('default')
    
    style_aplicacion_global.configure("Header.TFrame", background=config.COLOR_HEADER_BG)
    style_aplicacion_global.configure("Header.TLabel", background=config.COLOR_HEADER_BG, foreground=config.COLOR_HEADER_FG, font=("Arial", 20, "bold"), padding=(10,15))
    style_aplicacion_global.configure("TNotebook", background=config.COLOR_BACKGROUND, borderwidth=1)
    style_aplicacion_global.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[12, 6])
    style_aplicacion_global.map("TNotebook.Tab", background=[("selected", config.COLOR_TAB_ACTIVE_BG), ("!selected", config.COLOR_TAB_INACTIVE_BG)], foreground=[("selected", config.COLOR_TAB_ACTIVE_FG), ("!selected", config.COLOR_TAB_INACTIVE_FG)])
    style_aplicacion_global.configure("Content.TFrame", background=config.COLOR_BACKGROUND)
    style_aplicacion_global.configure("Search.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_TEXT_GENERAL, font=("Arial", 12, "bold"))
    style_aplicacion_global.configure("Search.TEntry", font=("Arial", 14), padding=(5,5))
    style_aplicacion_global.map("Search.TEntry", bordercolor=[('focus', config.COLOR_ACCENT)])
    style_aplicacion_global.configure("Info.Header.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_HEADER_BG, font=("Arial", 18, "bold"))
    style_aplicacion_global.configure("Info.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_TEXT_GENERAL, font=("Arial", 11))
    style_aplicacion_global.configure("Info.Bold.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_TEXT_GENERAL, font=("Arial", 11, "bold"))
    style_aplicacion_global.configure("Accent.TButton", font=("Arial", 11, "bold"), background=config.COLOR_ACCENT, foreground=config.COLOR_TEXT_ON_ACCENT, padding=(10,5), borderwidth=1)
    style_aplicacion_global.map("Accent.TButton", background=[('active', '#E88B0A'), ('pressed', '#D07D09')], relief=[('pressed', 'sunken'), ('!pressed', 'raised')])
    style_aplicacion_global.configure("Admin.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_ACCENT, font=("Arial", 10, "bold"), padding=5)
    style_aplicacion_global.configure("ErrorImage.TLabel", background=config.COLOR_BACKGROUND, foreground=config.COLOR_ERROR_TEXT, font=("Arial", 10, "italic"))

    frame_cabecera_main = ttk.Frame(app_principal_ref, style="Header.TFrame")
    frame_cabecera_main.pack(fill="x", side="top")
    ttk.Label(frame_cabecera_main, text="Balanzas Triunfo Enciclopedia", style="Header.TLabel").pack(pady=(5,10), side="left", padx=10)
    
    # Botón de Cerrar Sesión (siempre visible una vez logueado)
    btn_cerrar_sesion = ttk.Button(frame_cabecera_main, text="Cerrar Sesión", style="Accent.TButton", command=cerrar_sesion_ui)
    btn_cerrar_sesion.pack(side="right", padx=10, pady=10)

    if data_manager.usuario_actual["rol"] == "administrador":
        btn_gestion_usuarios = ttk.Button(frame_cabecera_main, text="Gestión de Usuarios", style="Accent.TButton", command=_abrir_ventana_gestion_usuarios_ui_accion)
        btn_gestion_usuarios.pack(side="right", padx=10, pady=10)

        btn_reg_prod = ttk.Button(frame_cabecera_main, text="Registrar Producto", style="Accent.TButton", command=_abrir_ventana_registrar_producto_ui_accion)
        btn_reg_prod.pack(side="right", padx=10, pady=10)
        lbl_total_stock_widget = ttk.Label(frame_cabecera_main, text="Stock Total Global: 0", style="Admin.TLabel")
        lbl_total_stock_widget.pack(side="right", padx=10, pady=10)
        _calcular_y_actualizar_total_stock_ui()

    notebook_main_frame = ttk.Frame(app_principal_ref, style="Content.TFrame", padding=(0,5,0,0))
    notebook_main_frame.pack(expand=True, fill='both')
    notebook_widget = ttk.Notebook(notebook_main_frame, style="TNotebook")
    
    tab_busqueda_main = ttk.Frame(notebook_widget, style="Content.TFrame", padding=20)
    notebook_widget.add(tab_busqueda_main, text='Buscar Producto')
    tab_info_producto_widget = ttk.Frame(notebook_widget, style="Content.TFrame", padding=0) 
    notebook_widget.add(tab_info_producto_widget, text='Información del Producto')
    notebook_widget.pack(expand=True, fill='both')

    ttk.Label(tab_busqueda_main, text="Ingrese el modelo de la balanza:", style="Search.TLabel").pack(pady=(0,10), anchor="w")
    entrada_modelo_busqueda_widget = ttk.Entry(tab_busqueda_main, style="Search.TEntry", width=45)
    entrada_modelo_busqueda_widget.pack(pady=(0,10), fill="x")
    entrada_modelo_busqueda_widget.bind("<KeyRelease>", actualizar_sugerencias_ui)
    
    frame_lista_sug = ttk.Frame(tab_busqueda_main, style="Content.TFrame")
    frame_lista_sug.pack(pady=10, fill="both", expand=True)
    lista_sugerencias_busqueda_widget = tk.Listbox(frame_lista_sug, font=("Arial", 12), width=38, height=10, bg=config.COLOR_LISTBOX_BG, fg=config.COLOR_LISTBOX_FG, selectbackground=config.COLOR_LISTBOX_SELECT_BG, selectforeground=config.COLOR_LISTBOX_SELECT_FG, borderwidth=1, relief="solid", exportselection=False)
    lista_sugerencias_busqueda_widget.pack(side="left", fill="both", expand=True)
    scrollbar_sug = ttk.Scrollbar(frame_lista_sug, orient="vertical", command=lista_sugerencias_busqueda_widget.yview)
    scrollbar_sug.pack(side="right", fill="y")
    lista_sugerencias_busqueda_widget.config(yscrollcommand=scrollbar_sug.set)
    lista_sugerencias_busqueda_widget.bind("<Double-Button-1>", mostrar_informacion_producto_seleccionado_ui)
    
    actualizar_sugerencias_ui()

    frame_info_producto_dinamico = ttk.Frame(tab_info_producto_widget, style="Content.TFrame")
    frame_info_producto_dinamico.pack(expand=True, fill='both')
    mostrar_informacion_producto_seleccionado_ui()
    
    entrada_modelo_busqueda_widget.focus()

def on_app_close_ui():
    """Maneja el cierre de la aplicación, registrando la acción."""
    if data_manager.hora_inicio_sesion_actual and data_manager.usuario_actual["nombre"]:
        duracion = datetime.datetime.now() - data_manager.hora_inicio_sesion_actual
        duracion_minutos = duracion.total_seconds() / 60
        registrar_accion_excel("Cierre Aplicacion", f"Usuario: {data_manager.usuario_actual.get('nombre', 'N/A')}", duracion_min=duracion_minutos)
    else:
        registrar_accion_excel("Cierre Aplicacion", "Sin inicio de sesion previo (cerrado desde login o sesion ya limpia).")
    
    if app_principal_ref:
        app_principal_ref.destroy()