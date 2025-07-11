# TP N°2 : Software Defined Networking (SDN)

## Contenido

Este proyecto implementa un entorno de red definido por software (SDN) utilizando Mininet y el controlador POX. Se desarrolla una topología personalizada y un firewall que instala reglas específicas en el switch s3 para controlar el tráfico entre hosts. El objetivo es experimentar con reglas de filtrado y observar su impacto en la conectividad y el tráfico de la red.

## Autores

| Nombre          | Apellido      | Mail                  | Padrón |
| --------------- | ------------- | --------------------- | ------ |
| Ian             | von der Heyde | ivon@fi.uba.ar        | 107638 |
| Agustín         | Altamirano    | aaltamirano@fi.uba.ar | 110237 |
| Juan Martín     | de la Cruz    | jdelacruz@fi.uba.ar   | 109588 |
| Cristhian David | Noriega       | cnoriega@fi.uba.ar    | 109164 |
| Santiago Tomás  | Fassio        | sfassio@fi.uba.ar     | 109463 |

---

## Requisitos

Para ejecutar este proyecto, asegurarse de tener instalados los siguientes paquetes en tu sistema basado en Debian/Ubuntu:

- **Python**: lenguaje de programación utilizado en el proyecto.
- **Mininet**: entorno de simulación de redes.
- **Open vSwitch Test Controller**: controlador simple para pruebas.
- **xterm**: terminal gráfica utilizada por Mininet.
- **Wireshark** (opcional): herramienta para capturar y analizar tráfico de red.

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

Para ajustar el tamaño de fuente de las terminales `xterm` (por ejemplo, utilizar la fuente _Monospace_ con tamaño 14), siga estos pasos:

1. Cree un archivo llamado `.Xresources` en su directorio personal (`/home/usuario/`) con el siguiente contenido:

   ```
   XTerm*faceName: Monospace
   XTerm*faceSize: 14
   ```

2. Aplique la configuración ejecutando el siguiente comando en una terminal:

   ```bash
   xrdb -merge ~/.Xresources
   ```

---

## Ejecuciones

A continuación se detallan las distintas partes para levantar el entorno, ejecutar pruebas y administrar el firewall.

### Levantar POX sin firewall

Esto inicia el controlador POX en modo básico, sin reglas de firewall.

```bash
python3.8 pox/pox.py log.level --DEBUG samples.spanning_tree
```

---

### Levantar POX con el módulo de firewall

Esto inicia POX cargando el módulo de firewall, que instala reglas de bloqueo en el switch s3.

```bash
PYTHONPATH=. python3.8 pox/pox.py firewall log.level --DEBUG samples.spanning_tree
```

---

### Crear la topología en Mininet

Esto crea una topología personalizada con 5 switches y 4 hosts, y conecta Mininet al controlador POX.

```bash
sudo mn --custom toupe.py --topo toupe,5 --controller remote,ip=localhost,port=6633 --arp --xterms
```

**Explicación de argumentos:**

- `--custom toupe.py`: Especifica el archivo Python que contiene la definición de topología personalizada
- `--topo toupe,5`: Utiliza la topología "toupe" definida en el archivo, creando una red con 5 switches
- `--controller remote,ip=localhost,port=6633`: Conecta la red simulada a un controlador SDN externo ejecutándose en la máquina local en el puerto 6633 (POX por defecto)
- `--arp`: Habilita el comportamiento automático de ARP, permitiendo que los hosts resuelvan direcciones MAC automáticamente.
- `--xterms`: (opcional) Abre una terminal xterm para cada host, facilitando la interacción con ellos

---

### Finalizar procesos en el puerto 6633

Si necesitas liberar el puerto 6633 (por ejemplo, si quedó ocupado por una instancia anterior de POX):

```bash
sudo lsof -i :6633
sudo kill -9 <PID>
```

Reemplaza `<PID>` por el número de proceso que aparece en la salida del primer comando.

---

### Verificar las reglas instaladas en el switch s3

Para inspeccionar y validar el funcionamiento del firewall, puedes utilizar los siguientes comandos de `ovs-ofctl`:

#### Mostrar todas las reglas de flujo instaladas

```bash
ovs-ofctl dump-flows s3
```

Este comando muestra todas las reglas de flujo activas en el switch s3, incluyendo:

- **Prioridad** de cada regla (las reglas del firewall tienen prioridad 100)
- **Criterios de coincidencia** (MAC, IP, protocolo, puertos, etc.)
- **Acciones** a realizar (DROP para bloquear, NORMAL para permitir)
- **Estadísticas** de uso (cantidad de paquetes y bytes procesados)

#### Mostrar estadísticas de puertos

```bash
ovs-ofctl dump-ports s3
```

Proporciona estadísticas detalladas de cada puerto del switch, incluyendo:

- Paquetes transmitidos y recibidos
- Bytes transferidos
- Errores y descartes
- Velocidad de transmisión

#### Mostrar información general del switch

```bash
ovs-ofctl show s3
```

Muestra la configuración general del switch:

- Puertos disponibles y su estado
- Conexión con el controlador
- Capacidades soportadas

---

### Pruebas sugeridas

A continuación, se listan pruebas para verificar el funcionamiento de la red y del firewall.

#### a) Prueba de conectividad general

```bash
mininet> pingall
```

#### b) Pruebas de tráfico bloqueado por el firewall

**Iperf en puerto 80 (UDP):**

```bash
xterm> iperf -s -u -p 80
xterm> iperf -c <IP_destino> -u -p 80
```

**Iperf en puerto 80 (TCP):**

```bash
xterm> iperf -s -p 80
xterm> iperf -c <IP_destino> -p 80
```

**Iperf entre h1 y h3:**

```bash
xterm> iperf -s
xterm> iperf -c <IP_h1> -p <puerto>
```

**Iperf entre h3 y h1:**

```bash
xterm> iperf -s
xterm> iperf -c <IP_h1> -p <puerto>
```

**Iperf desde h1 a h3/h4 en puerto 5001 (UDP):**

```bash
xterm> iperf -s -u -p 5001
xterm> iperf -c <IP_h3_o_h4> -u -p 5001
```

---

### Notas importantes

- **Las reglas de firewall se instalan únicamente en el switch s3.**
- Puedes modificar las reglas editando el archivo `rules.json` y reiniciando el controlador POX.
- Para ver la tabla de flujos en otros switches, cambia `s3` por el nombre del switch deseado en los comandos de `ovs-ofctl`.

---

### Campos disponibles en las reglas de flujo

| Campo         | Tipo                             | Descripción                                                         |
| ------------- | -------------------------------- | ------------------------------------------------------------------- |
| `dl_src`      | `EthAddr`                        | Dirección MAC de origen                                             |
| `dl_dst`      | `EthAddr`                        | Dirección MAC de destino                                            |
| `dl_type`     | `int` (hex)                      | Tipo de protocolo de capa 2 (ej: 0x0800 para IPv4, 0x0806 para ARP) |
| `dl_vlan`     | `int`                            | ID de VLAN (802.1Q)                                                 |
| `dl_vlan_pcp` | `int`                            | Prioridad de VLAN                                                   |
| `nw_src`      | `IPAddr` o `IPAddr("x.x.x.x/x")` | IP de origen                                                        |
| `nw_dst`      | `IPAddr`                         | IP de destino                                                       |
| `nw_proto`    | `int`                            | Protocolo de capa 3 (ej: 1 para ICMP, 6 para TCP, 17 para UDP)      |
| `nw_tos`      | `int` (0-255)                    | Type of Service (ToS) de IP                                         |
| `tp_src`      | `int`                            | Puerto de origen TCP o UDP                                          |
| `tp_dst`      | `int`                            | Puerto de destino TCP o UDP                                         |
| `in_port`     | `int`                            | Puerto de entrada en el switch                                      |
