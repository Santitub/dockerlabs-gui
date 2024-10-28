import os
import shutil
import subprocess
import time
from colorama import Fore, Style, init
import sys
import threading

class DockerDeployment:
    def __init__(self, machine_name):
        self.machine_name = machine_name
        self.deploy_folder = "./despliegue"  # Carpeta donde se extraen las máquinas
        self.tar_file = os.path.join(self.deploy_folder, f"{self.machine_name}")  # Ruta al archivo .tar
        self.container_name = None
        init()  # Inicializa colorama para el uso de colores en Windows

    @staticmethod
    def print_banner():
        print("\n")
        print(f"\t                   {Fore.RED} ##       {Fore.WHITE} .         ")
        print(f"\t             {Fore.RED} ## ## ##      {Fore.WHITE} ==         ")
        print(f"\t           {Fore.RED}## ## ## ##      {Fore.WHITE}===         ")
        print(f'\t       /""""""""""""""""""\\___/ ===       ')
        print(f'\t  {Fore.BLUE}~~~ {Fore.WHITE}{{{Fore.BLUE}~~ ~~~~ ~~~ ~~~~ ~~ ~ {Fore.WHITE}/  ===- {Fore.BLUE}~~~{Fore.WHITE}}} ')
        print(f'\t       \\______{Fore.WHITE} o {Fore.WHITE}         __/           ')
        print(f'\t         \\    \\        __/            ')
        print(f'\t          \\____\\______/               ')
        print(f"{Style.BRIGHT}{Fore.CYAN}")
        print(r"  ___  ____ ____ _  _ ____ ____ _    ____ ___  ____ ")
        print(r"  |  \ |  | |    |_/  |___ |__/ |    |__| |__] [__  ")
        print(r"  |__/ |__| |___ | \_ |___ |  \ |___ |  | |__] ___] ")
        print(f"{Style.RESET_ALL}")
        print(f"\t\t\t\t  {Fore.RED} {Fore.YELLOW} {Style.RESET_ALL}")

    @staticmethod
    def verificar_instalacion_docker():
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"{Style.BRIGHT}{Fore.CYAN}\nDocker no está instalado. Instalando Docker...{Fore.YELLOW}{Style.RESET_ALL}")
            subprocess.run(["sudo", "apt", "update"])
            subprocess.run(["sudo", "apt", "install", "docker.io", "-y"])
            print(f"{Style.BRIGHT}{Fore.CYAN}\nEstamos habilitando el servicio de docker. Espere un momento...{Fore.YELLOW}{Style.RESET_ALL}")
            time.sleep(10)
            if subprocess.run(["systemctl", "restart", "docker"]).returncode == 0 and subprocess.run(["systemctl", "enable", "docker"]).returncode == 0:
                print(f"{Style.BRIGHT}{Fore.LIGHTGREEN_EX}\nDocker ha sido instalado correctamente.")
            else:
                print("Error al instalar Docker. Por favor, verifique y vuelva a intentarlo.")
                sys.exit(1)

    def detener_y_eliminar_contenedor(self):
        image_name = os.path.basename(self.tar_file).replace(".tar", "")
        container_name = f"{image_name}_container"
        self.container_name = container_name

        if subprocess.run(["docker", "ps", "-a", "-q", "-f", f"name={container_name}", "-f", "status=exited"], stdout=subprocess.PIPE).stdout:
            subprocess.run(["docker", "rm", container_name])

        if subprocess.run(["docker", "ps", "-q", "-f", f"name={container_name}"], stdout=subprocess.PIPE).stdout:
            subprocess.run(["docker", "stop", container_name])
            subprocess.run(["docker", "rm", container_name])

        if subprocess.run(["docker", "images", "-q", image_name], stdout=subprocess.PIPE).stdout:
            subprocess.run(["docker", "rmi", image_name])
    
    def detener_todos_los_contenedores():
        # Obtener todos los contenedores en ejecución
        running_containers = subprocess.run(
            ["docker", "ps", "-q"],
            stdout=subprocess.PIPE,
            text=True
        ).stdout.strip().splitlines()

        # Detener y eliminar todos los contenedores en ejecución
        if running_containers:
            print(f"{Style.BRIGHT}{Fore.YELLOW}Se han detectado contenedores en ejecución. Cerrándolos...{Style.RESET_ALL}")
            for container in running_containers:
                subprocess.run(["docker", "stop", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["docker", "rm", container], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Style.BRIGHT}{Fore.CYAN}Todos los contenedores han sido detenidos y eliminados.{Style.RESET_ALL}")
        else:
            print(f"{Style.BRIGHT}{Fore.CYAN}No hay contenedores en ejecución actualmente.{Style.RESET_ALL}")

    def limpiar_imagenes_docker(self):
        base_name = os.path.basename(self.tar_file).replace('.tar', '')
        image_id = subprocess.run(
            ["docker", "images", "-q", base_name],
            capture_output=True,
            text=True
        ).stdout.strip()

        if image_id:
            print(f"{Style.BRIGHT}{Fore.YELLOW}\nSe han detectado imágenes previas de Docker. Eliminándolas...{Style.RESET_ALL}")
            subprocess.run(["docker", "rmi", "-f", image_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{Style.BRIGHT}{Fore.CYAN}Las imágenes previas han sido eliminadas.{Style.RESET_ALL}")
        else:
            print(f"{Style.BRIGHT}{Fore.CYAN}No hay imágenes previas de Docker.{Style.RESET_ALL}")

    def signal(self):
        print(f"{Style.BRIGHT}{Fore.WHITE}\nEliminando el laboratorio, espere un momento...{Style.RESET_ALL}")
        thread = threading.Thread(target=self.detener_y_eliminar_contenedor)
        thread.start()
        thread.join()
        
        print(f"{Style.BRIGHT}{Fore.WHITE}\nEl laboratorio ha sido eliminado por completo del sistema.{Style.RESET_ALL}")
        sys.exit(0)

    def deploy(self, output_callback=None):
        if not os.path.exists(self.tar_file):
            print(f"{Fore.RED}No se encontró el archivo {self.tar_file}. Asegúrate de que está en la carpeta 'despliegue'.{Style.RESET_ALL}")
            return

        self.detener_y_eliminar_contenedor()
        self.limpiar_imagenes_docker()
        print(f"{Style.BRIGHT}{Fore.YELLOW}\nEstamos desplegando la máquina vulnerable, espere un momento.{Style.RESET_ALL}")

        if subprocess.run(["docker", "load", "-i", self.tar_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            image_name = os.path.basename(self.tar_file).replace(".tar", "")
            container_name = f"{image_name}_container"
            self.container_name = container_name

            if output_callback:
                output_callback(f"{Style.BRIGHT}{Fore.CYAN}\nMáquina desplegada correctamente.\n")

            if "arm" in os.uname().machine:
                subprocess.run(["apt", "install", "--assume-yes", "binfmt-support", "qemu-user-static", "-y"])
                subprocess.run(["docker", "run", "--platform", "linux/amd64", "-d", "--name", container_name, image_name])
            else:
                subprocess.run(["docker", "run", "-d", "--name", container_name, image_name])

            ip_address = subprocess.run(
                ["docker", "inspect", "-f", "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}", container_name],
                stdout=subprocess.PIPE
            ).stdout.decode().strip()

            print(f"{Style.BRIGHT}{Fore.CYAN}\nMáquina desplegada, su dirección IP es --> {Fore.WHITE}{ip_address}{Style.RESET_ALL}")
            print(f"{Style.BRIGHT}{Fore.RED}\nPresiona el botón cuando termines con la máquina para eliminarla.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}\nHa ocurrido un error al cargar el laboratorio en Docker.{Style.RESET_ALL}")
            sys.exit(1)