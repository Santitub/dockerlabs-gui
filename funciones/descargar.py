from funciones.download.mega import Mega
import threading
import subprocess

nombre_archivo = ""

def iniciar_descarga(link, app):
    threading.Thread(target=descargar_archivo_mega, args=(link, app)).start()

def descargar_archivo_mega(link, app):
    app.progress_label.configure(text="Iniciando sesión en Mega...")
    mega = Mega()

    try:
        m = mega.login()
        archivo_info = m.get_public_url_info(link)
        nombre_archivo = archivo_info['name']
        tamano_archivo = archivo_info['size']

        app.progress_label.configure(text=f"Descargando {nombre_archivo}...")
        m.download_url(link, dest_filename=nombre_archivo, progress_callback=lambda t, tt: actualizar_progreso(t, tt, app))

        app.progress_label.configure(text=f"Descarga completa: {nombre_archivo}")
        subprocess.run("sudo", "chmod" , "666" , nombre_archivo)

    except Exception as e:
        app.progress_label.configure(text=f"Error: {e}")

def actualizar_progreso(tamano_descargado, tamano_total, app):
    tamano_descargado_mb = tamano_descargado / (1024 * 1024)
    tamano_total_mb = tamano_total / (1024 * 1024)
    app.progress_label.configure(text=f"Progreso: {tamano_descargado_mb:.2f} MB / {tamano_total_mb:.2f} MB") 