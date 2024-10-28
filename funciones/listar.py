import os
import unidecode
import requests
from bs4 import BeautifulSoup
import tkinter as tk
import subprocess
import getpass  # Para obtener el nombre del usuario actual

# URL de la página web de DockerLabs
URL = 'https://dockerlabs.es'

# Archivo local para almacenar las máquinas
ARCHIVO_MAQUINAS = "maquinas.txt"
CARPETA_MAQUINAS = "maquinas"
DIFICULTAD = ("muy facil", "facil", "medio", "dificil")

def crear_archivo_maquinas():
    """Crear el archivo 'maquinas.txt' si no existe."""
    if not os.path.exists(ARCHIVO_MAQUINAS):
        with open(ARCHIVO_MAQUINAS, "w") as file:
            file.write("")  # Crear un archivo vacío
        
    os.chmod(ARCHIVO_MAQUINAS, 0o777)  # Permisos: lectura y escritura para usuario y grupo

def crear_carpeta_si_no_existe(carpeta):
    """Crear una carpeta con permisos adecuados si no existe."""
    if not os.path.exists(carpeta):
        os.makedirs(carpeta, exist_ok=True)
    os.chmod(carpeta, 0o777)  # Permisos de lectura, escritura y ejecución para usuario y grupo

def guardar_maquinas_archivo(machines):
    """Guardar la información de las máquinas en el archivo 'maquinas.txt'."""
    with open(ARCHIVO_MAQUINAS, "w") as file:
        for machine in machines:
            file.write(f"{machine['nombre']} | {machine['fecha']} | {machine['creador']} | {machine['dificultad']}\n")

def list_local_machines(treeview):
    """Listar máquinas locales almacenadas en el sistema y completar su información desde el archivo."""
    folders = ["completadas", "por hacer"]
    downloaded_machines = []

    for folder in folders:
        folder_path = os.path.join(CARPETA_MAQUINAS, folder)
        crear_carpeta_si_no_existe(folder_path)

        for dificultad in DIFICULTAD:
            dificultad_path = os.path.join(folder_path, dificultad)
            crear_carpeta_si_no_existe(dificultad_path)
            
            for filename in os.listdir(dificultad_path):
                if filename.endswith(".zip"):
                    machine_name = filename[:-4].lower()  # Quitar la extensión .zip
                    downloaded_machines.append((machine_name, dificultad.lower()))

    downloaded_machines_info = completar_info_desde_archivo(downloaded_machines)

    for machine_name, fecha_creacion, creador, dificultad, descargada in downloaded_machines_info:
        treeview.insert("", "end", values=(
            machine_name.title(), 
            fecha_creacion, 
            creador.title(), 
            dificultad.title(), 
            descargada
        ))

    return downloaded_machines_info

def list_deployable_machines(deploy_machines):
    """Listar máquinas descargadas y mostrar en el Treeview 'deploy_machines'."""
    folders = ["completadas", "por hacer"]
    downloaded_machines = []

    for folder in folders:
        folder_path = os.path.join(CARPETA_MAQUINAS, folder)
        if os.path.exists(folder_path):  # Verificar si la carpeta existe
            for dificultad in os.listdir(folder_path):
                dificultad_path = os.path.join(folder_path, dificultad)
                if os.path.exists(dificultad_path):  # Verificar si la carpeta de dificultad existe
                    for filename in os.listdir(dificultad_path):
                        if filename.endswith(".zip"):
                            machine_name = filename[:-4].lower()  # Quitar la extensión .zip
                            downloaded_machines.append((machine_name, dificultad.lower()))

    downloaded_machines_info = completar_info_desde_archivo(downloaded_machines)

    for machine_name, _, _, dificultad, _ in downloaded_machines_info:  # Ignorar otros valores
        deploy_machines.insert("", "end", values=(
            machine_name.title(), 
            dificultad.title()
        ))

    return downloaded_machines_info

def completar_info_desde_archivo(downloaded_machines):
    """Completar la información de las máquinas descargadas usando el archivo 'maquinas.txt'."""
    machines_info = leer_maquinas_archivo()

    completed_info = []
    for machine_name, dificultad in downloaded_machines:
        creador = 'Desconocido'
        fecha_creacion = 'Desconocida'
        descargada = "✔️"

        for machine in machines_info:
            if machine['nombre'] == machine_name and machine['dificultad'] == dificultad:
                creador = machine['creador']
                fecha_creacion = machine['fecha']
                break

        completed_info.append((machine_name, fecha_creacion, creador, dificultad, descargada))

    return completed_info

def leer_maquinas_archivo():
    """Leer la información de las máquinas desde el archivo 'maquinas.txt'."""
    machines_info = []
    if os.path.exists(ARCHIVO_MAQUINAS):
        with open(ARCHIVO_MAQUINAS, "r") as file:
            for line in file:
                nombre, fecha, creador, dificultad = line.strip().split(" | ")
                machines_info.append({
                    'nombre': nombre.lower(),
                    'fecha': fecha,
                    'creador': creador.lower(),
                    'dificultad': dificultad.lower()
                })
    return machines_info

def list_web_machines(treeview, downloaded_machines):
    """
    Listar máquinas disponibles en la web que no estén descargadas.
    Se muestra en el 'treeview' con el formato especificado.
    """
    docker_rows = obtener_datos_web()
    machines = []

    # Normalizamos los nombres y dificultades de las máquinas descargadas para la comparación
    downloaded_machines_set = set((name.lower(), difficulty.lower()) for name, _, _, difficulty, _ in downloaded_machines)

    for row in docker_rows:
        name = row.find("span").find("strong")
        difficulty = row.find("span", class_="badge")
        onclick_text = row.attrs.get('onclick')
        creador_text = 'n/a'
        fecha_creacion = 'n/a'

        if onclick_text:
            creador_text = obtener_elemento_onclick(onclick_text, 3).lower()
            fecha_creacion = obtener_elemento_onclick(onclick_text, 5).lower()

        name_text = name.get_text(strip=True).lower() if name else 'n/a'
        difficulty_text = unidecode.unidecode(difficulty.get_text(strip=True)).lower() if difficulty else 'n/a'

        # Solo agregar máquinas que no estén en la lista de descargadas
        if (name_text, difficulty_text) not in downloaded_machines_set:
            treeview.insert("", "end", values=(
                name_text.title(), 
                fecha_creacion, 
                creador_text.title(), 
                difficulty_text.title(), 
                "No"  # Las máquinas web aún no están descargadas
            ))

        machines.append({
            'nombre': name_text,
            'fecha': fecha_creacion,
            'creador': creador_text,
            'dificultad': difficulty_text
        })

    # Guardar todas las máquinas en el archivo
    guardar_maquinas_archivo(machines)

def obtener_elemento_onclick(text, index):
    """Función para extraer el elemento correcto del atributo onclick."""
    try:
        elementos = text.split('(')[1].split(')')[0].split(',')
        return elementos[index].strip().strip("'").strip('"').lower()
    except (IndexError, AttributeError):
        return 'n/a'

def obtener_datos_web():
    """Obtener datos de las máquinas desde la web usando scraping."""
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"[x] Error al acceder a la página: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    return soup.find_all("div", class_=lambda x: x and "item" in x.split())