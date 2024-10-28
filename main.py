import customtkinter as ctk
import tkinter as tk
from tkinter import ttk  # Para usar Treeview
import subprocess
import os
import shutil
import zipfile
import threading
from funciones.listar import list_local_machines, crear_archivo_maquinas, list_web_machines, list_deployable_machines
from funciones.deploy import deploy, stop
from funciones.descargar import iniciar_descarga

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gestor de Máquinas")
        self.geometry("800x600")

        # Barra lateral
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="Opciones")
        self.sidebar_label.pack(pady=10)

        options = ["Máquinas disponibles", "Desplegar máquina", "Descargar máquina"]
        for option in options:
            button = ctk.CTkButton(self.sidebar, text=option, command=lambda opt=option: self.show_option(opt))
            button.pack(pady=5)

        # Contenido principal
        self.main_content = ctk.CTkFrame(self)
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.current_frame = None
        self.console_output = None  # Inicializar el atributo para la consola
        self.treeview = None  # Treeview para mostrar las máquinas

        self.show_option("Máquinas disponibles")

    def show_option(self, option):
        if self.current_frame:
            self.current_frame.pack_forget()

        if option == "Máquinas disponibles":
            self.current_frame = self.create_available_machines_frame()
        elif option == "Desplegar máquina":
            self.current_frame = self.create_deploy_machine_frame()
        elif option == "Descargar máquina":
            self.current_frame = self.create_download_frame()

        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def create_available_machines_frame(self):
        frame = ctk.CTkFrame(self.main_content)

        # Crear y configurar el Treeview como tabla
        self.machine_table = ttk.Treeview(frame, columns=("Nombre", "Fecha", "Creador", "Dificultad", "Descargada"), show="headings", height=15)
        self.machine_table.heading("Nombre", text="Nombre", anchor="center")
        self.machine_table.heading("Fecha", text="Fecha de creación", anchor="center")
        self.machine_table.heading("Creador", text="Creador", anchor="center")
        self.machine_table.heading("Dificultad", text="Dificultad", anchor="center")
        self.machine_table.heading("Descargada", text="Descargada", anchor="center")

        self.machine_table.column("Nombre", width=150, anchor="center")
        self.machine_table.column("Fecha", width=150, anchor="center")
        self.machine_table.column("Creador", width=150, anchor="center")
        self.machine_table.column("Dificultad", width=100, anchor="center")
        self.machine_table.column("Descargada", width=100, anchor="center")

        self.machine_table.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Estilos de Treeview
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="blue", background="lightgray", anchor="center")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[('selected', '#73c2fb')])

        # Variables para las opciones de mostrar descargadas y web
        self.descargadas_var = tk.BooleanVar(value=True)
        self.web_var = tk.BooleanVar(value=True)

        descargadas_button = ctk.CTkCheckBox(frame, text="Descargadas", variable=self.descargadas_var, command=self.update_machines_list)
        web_button = ctk.CTkCheckBox(frame, text="Web", variable=self.web_var, command=self.update_machines_list)

        descargadas_button.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        web_button.grid(row=1, column=0, sticky="e", padx=10, pady=5)

        # Crear el archivo antes de listar
        crear_archivo_maquinas()

        self.update_machines_list()

        return frame
    
    def update_machines_list(self):
        # Limpiar la tabla
        for row in self.machine_table.get_children():
            self.machine_table.delete(row)

        downloaded_machines = []
        if self.descargadas_var.get():
            downloaded_machines = list_local_machines(self.machine_table)

        if self.web_var.get():
            list_web_machines(self.machine_table, downloaded_machines)
    
    def update_deployable_machines_list(self):
        for row in self.deploy_machines.get_children():
            self.deploy_machines.delete(row)
        
        list_deployable_machines(self.deploy_machines)

    def create_deploy_machine_frame(self):
        frame = ctk.CTkFrame(self.main_content)

        # Crear y configurar el Treeview como tabla
        self.deploy_machines = ttk.Treeview(frame, columns=("Nombre", "Dificultad"), show="headings", height=15)
        self.deploy_machines.heading("Nombre", text="Nombre", anchor="center")
        self.deploy_machines.heading("Dificultad", text="Dificultad", anchor="center")

        self.deploy_machines.column("Nombre", width=150, anchor="center")
        self.deploy_machines.column("Dificultad", width=150, anchor="center")

        self.deploy_machines.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.deploy_machines.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Estilos de Treeview
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), foreground="blue", background="lightgray", anchor="center")
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        style.map("Treeview", background=[('selected', '#73c2fb')])

        self.update_deployable_machines_list()

        # Botón para desplegar la máquina seleccionada
        deploy_button = ctk.CTkButton(frame, text="Desplegar Máquina", command=self.deploy_selected_machine)
        deploy_button.pack(pady=10)

        # Botón para detener y eliminar la máquina
        stop_button = ctk.CTkButton(frame, text="Detener y Eliminar Máquina", command=self.stop_selected_machine)
        stop_button.pack(pady=10)

        # Caja de texto para mostrar la salida
        self.console_output = ctk.CTkTextbox(frame, height=200, width=400, wrap="word")
        self.console_output.pack(side=tk.LEFT, fill=tk.X, expand=False)

        return frame

    def deploy_selected_machine(self):

        # Definir la carpeta de despliegue
        deploy_folder = "./despliegue"

        # Eliminar la carpeta de despliegue si existe
        delete_thread = threading.Thread(target=self.delete_deploy_folder, args=(deploy_folder,))
        delete_thread.start()
        delete_thread.join()  # Espera a que el hilo termine la eliminación

        selected_item = self.deploy_machines.selection()  # Obtener la selección del Treeview
        if selected_item:
            # Obtener los valores de la fila seleccionada
            machine_data = self.deploy_machines.item(selected_item[0], 'values')
            
            if machine_data:
                selected_machine = machine_data[0].lower()  # Nombre de la máquina seleccionada
                print("Máquina seleccionada:", selected_machine)
                
                # Buscar el archivo .zip de la máquina
                result = subprocess.run(
                    ["find", ".", "-type", "f", "-name", f"{selected_machine}*.zip"], 
                    capture_output=True, 
                    text=True
                )
                
                # Obtener la ruta del archivo encontrado
                final_machine = result.stdout.strip().splitlines()
                if final_machine:
                    zip_path = final_machine[0]  # Asumimos que el primer resultado es el correcto
                    print("Archivo encontrado:", zip_path)

                    # Verificar que la carpeta realmente no existe antes de proceder
                    if not os.path.exists(deploy_folder):
                        # Crear la carpeta de despliegue
                        os.makedirs(deploy_folder, exist_ok=True)
                        
                        # Copiar el archivo .zip a la carpeta de despliegue
                        destination_zip = os.path.join(deploy_folder, os.path.basename(zip_path))
                        shutil.copy2(zip_path, destination_zip)
                        print("Archivo copiado a la carpeta de despliegue.")
                        
                        # Extraer el archivo .zip en la carpeta de despliegue
                        with zipfile.ZipFile(destination_zip, 'r') as zip_ref:
                            zip_ref.extractall(deploy_folder)
                        print("Archivo extraído en la carpeta de despliegue.")
                        
                        # Ejecutar el despliegue
                        deploy(selected_machine)  # Llamada a la función de despliegue con la ruta de despliegue
                    else:
                        print("Error: No se pudo eliminar la carpeta de despliegue.")
                else:
                    print("No se encontró un archivo .zip para la máquina seleccionada.")

    def delete_deploy_folder(self, folder_path):
        """Elimina la carpeta de despliegue de manera segura."""
        if os.path.exists(folder_path):
            subprocess.run(["sudo", "rm", "-rf", folder_path])

    def stop_selected_machine(self):
        selected_item = self.deploy_machines.selection()  # Obtener la selección del Treeview
        if selected_item:
            # Obtener los valores de la fila seleccionada
            machine_data = self.deploy_machines.item(selected_item[0], 'values')
            
            if machine_data:
                selected_machine = machine_data[0].lower()  # Nombre de la máquina seleccionada
                print("Máquina seleccionada:", selected_machine)
                stop(selected_machine)
            
    def create_download_frame(self):
        frame = ctk.CTkFrame(self.main_content)

        # Etiqueta y campo de entrada para el enlace de Mega
        self.label_link = ctk.CTkLabel(frame, text="Introduce el link de Mega:")
        self.label_link.pack(pady=10)

        self.entry_link = ctk.CTkEntry(frame, width=300)
        self.entry_link.pack(pady=10)

        # Botón de descarga, que inicia el proceso llamando a `iniciar_descarga`
        self.download_button = ctk.CTkButton(
            frame, 
            text="Descargar", 
            command=lambda: iniciar_descarga(self.entry_link.get(), self)
        )
        self.download_button.pack(pady=10)

        # Etiqueta de progreso
        self.progress_label = ctk.CTkLabel(frame, text="Progreso: 0 MB / 0 MB")
        self.progress_label.pack(pady=10)

        return frame

if __name__ == "__main__":
    app = App()
    app.mainloop()