# DOCKERLABS GUI

*SE RECOMIENDA USAR **KALI LINUX** PARA USAR ESTE PROGRAMA*

```bash
git clone https://github.com/Santitub/dockerlabs-gui.git

cd dockerlabs-gui

pip3 install -r requirements.txt 
```
### IMPORTANTE !!!

La función de **download** es la librería [mega.py](https://github.com/odwyersoftware/mega.py) pero con algunas modificaciones que me ayudaron a hacer el progreso de descarga (modifiqué los parámetros de la descarga para que se descargaran por chunks).

# No desplieguen máquinas mientras tengan un contenedor suspendido ya que este se borrará

---

**Creado en** ![python](https://img.shields.io/badge/python-3.12.9-3670A0?logo=python&logoColor=ffdd54)

Este programa puede:
- Listar todas las máquinas disponibles en [DockerLabs](https://dockerlabs.es) , tanto descargadas como no descargadas.
- Desplegar una máquina desde la interfaz (por ahora no está soportado para desplegar varias a la vez)
- Descargar una máquina pasándole el enlace de mega.

## Uso

```
sudo python3 main.py
```
**Es importante ejecutar el programa con** **```sudo```** **ya que de lo contrario no funcionará correctamente. Tanto si descargas el código fuente como el ejecutable**

## Imágenes

![listar](https://github.com/user-attachments/assets/46dd4bd1-9f88-4190-a1e0-53b94363469a)

![desplegar](https://github.com/user-attachments/assets/36d40437-b45c-4f9d-a0d5-5dcbbbe37f10)

![descargar](https://github.com/user-attachments/assets/4f1406ec-567b-4241-a1eb-9d525d9e24d4)
