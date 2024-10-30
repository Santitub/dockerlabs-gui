from funciones.download.mega import Mega
import threading
import shutil
import os
from funciones.listar import leer_maquinas_archivo

def iniciar_descarga(link, app):
    threading.Thread(target=descargar_archivo_mega, args=(link, app)).start()

def descargar_archivo_mega(link, app):
    app.progress_label.configure(text="Iniciando sesión en Mega...")
    mega = Mega()

    try:
        # Inicia sesión y obtiene información del archivo
        m = mega.login()
        archivo_info = m.get_public_url_info(link)
        nombre_archivo_original = archivo_info['name']
        nombre_archivo_sin_extension = os.path.splitext(nombre_archivo_original)[0]
        
        # Establece el nombre del archivo descargado con la extensión .zip
        nombre_archivo_zip = f"{nombre_archivo_sin_extension}.zip"

        # Configura progreso de la descarga
        app.progress_label.configure(text=f"Descargando {nombre_archivo_zip}...")
        m.download_url(link, dest_filename=nombre_archivo_zip, progress_callback=lambda t, tt: actualizar_progreso(t, tt, app))

        # Configuración final de permisos
        app.progress_label.configure(text=f"Descarga completa: {nombre_archivo_zip}")
        os.chmod(nombre_archivo_original, 0o777)
        print(obtener_datos(nombre_archivo_sin_extension))

    except Exception as e:
        app.progress_label.configure(text=f"Error: {e}")

def actualizar_progreso(tamano_descargado, tamano_total, app):
    tamano_descargado_mb = tamano_descargado / (1024 * 1024)
    tamano_total_mb = tamano_total / (1024 * 1024)
    app.progress_label.configure(text=f"Progreso: {tamano_descargado_mb:.2f} MB / {tamano_total_mb:.2f} MB")

def obtener_datos(nombre_archivo_sin_extension):
    # Obtiene la lista de máquinas desde el archivo
    maquinas = leer_maquinas_archivo()

    # Filtra la máquina específica por nombre (sin extensión)
    datos_maquina = [(maquina['nombre'], maquina['dificultad']) for maquina in maquinas if maquina['nombre'].lower() == nombre_archivo_sin_extension.lower()]

    # Verifica si la máquina fue encontrada en el archivo de datos
    if not datos_maquina:
        return f"No se encontraron datos para la máquina con nombre '{nombre_archivo_sin_extension}'."

    # Verifica si el archivo .zip existe en el sistema de archivos
    nombre_archivo_zip = f"{nombre_archivo_sin_extension}.zip"
    if os.path.exists(nombre_archivo_zip):
        # Obtiene la dificultad de la máquina y define la ruta de destino
        dificultad = datos_maquina[0][1]
        ruta_destino = os.path.join('maquinas/por hacer/', dificultad)

        # Crea la carpeta de destino si no existe
        os.makedirs(ruta_destino, exist_ok=True)

        # Mueve el archivo a la carpeta de dificultad
        destino_archivo = os.path.join(ruta_destino, nombre_archivo_zip)
        shutil.move(nombre_archivo_zip, destino_archivo)

        # Devuelve los datos de la máquina
        return {
            'nombre': datos_maquina[0][0],
            'dificultad': dificultad,
            'ruta_destino': destino_archivo
        }
    else:
        return f"El archivo '{nombre_archivo_zip}' no existe en el sistema."