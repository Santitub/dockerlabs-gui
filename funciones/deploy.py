from funciones.auto_deploy import DockerDeployment
import threading

# Function to trigger deploy on button press
def deploy(selected_machine):
    DockerDeployment.print_banner()
    DockerDeployment.verificar_instalacion_docker()
    DockerDeployment.detener_todos_los_contenedores()
    deploy_manager = DockerDeployment(f'{selected_machine}.tar')
    threading.Thread(target=deploy_manager.deploy).start()

# Function to trigger stop and remove container
def stop(selected_machine):
    deploy_manager = DockerDeployment(f'{selected_machine}.tar')
    threading.Thread(target=deploy_manager.signal).start()