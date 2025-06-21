# TP N°2 : Software Defined Networking (SDN)

## Contenido

In progress...

## Autores

| Nombre          | Apellido      | Mail                  | Padrón |
| --------------- | ------------- | --------------------- | ------ |
| Ian             | von der Heyde | ivon@fi.uba.ar        | 107638 |
| Agustín         | Altamirano    | aaltamirano@fi.uba.ar | 110237 |
| Juan Martín     | de la Cruz    | jdelacruz@fi.uba.ar   | 109588 |
| Cristhian David | Noriega       | cnoriega@fi.uba.ar    | 109164 |
| Santiago Tomás  | Fassio        | sfassio@fi.uba.ar     | 109463 |

## Estructura del repositorio

```
 📁 FIUBA-REDES-TP2/ 
  ├── 📄 README.md                         # Documento principal con instrucciones de uso y ejecución
  ├── 📊 Informe.pdf                       # Informe académico que detalla el desarrollo del trabajo práctico
  ├── 📂 docs/...                          # Archivos complementarios para la documentación
  └── 📂 src/                              # Código fuente principal del proyecto

```

---

## Requisitos

Para ejecutar este proyecto, asegurarse de tener instalados los siguientes paquetes en tu sistema basado en Debian/Ubuntu:

- **Python**: lenguaje de programación utilizado en el proyecto.
- **Mininet**: entorno de simulación de redes.
- **Open vSwitch Test Controller**: controlador simple para pruebas.
- **xterm**: terminal gráfica utilizada por Mininet.
-  **Wireshark** (opcional): herramienta para capturar y analizar tráfico de red.

Puedes instalarlos con los siguientes comandos:

```bash
sudo apt install python3
sudo apt install openvswitch-testcontroller
sudo ln -s /usr/bin/ovs-testcontroller /usr/bin/controller
sudo apt install mininet
sudo apt install xterm  
sudo apt install wireshark
```

### (Opcional) Configurar tamaño de fuente de xterm

Para ajustar el tamaño de fuente de las terminales `xterm` (por ejemplo, utilizar la fuente *Monospace* con tamaño 14), siga estos pasos:

1. Cree un archivo llamado `.Xresources` en su directorio personal (`/home/usuario/`) con el siguiente contenido:

    ```
    XTerm*faceName: Monospace
    XTerm*faceSize: 14
    ```

2. Aplique la configuración ejecutando el siguiente comando en una terminal:

    ```bash
    xrdb -merge ~/.Xresources
    ```

