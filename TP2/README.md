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

## Ejecución paso a paso

A continuación se detallan los pasos para levantar el entorno, ejecutar pruebas y administrar el firewall.

### 1. Levantar POX sin firewall

Esto inicia el controlador POX en modo básico, sin reglas de firewall.

```bash
python3.8 pox/pox.py log.level --DEBUG samples.spanning_tree
```

---

### 2. Levantar POX con el módulo de firewall

Esto inicia POX cargando el módulo de firewall, que instala reglas de bloqueo en el switch s3.

```bash
PYTHONPATH=. python3.8 pox/pox.py firewall log.level --DEBUG samples.spanning_tree
```

---

### 3. Crear la topología en Mininet

Esto crea una topología personalizada con 5 switches y 4 hosts, y conecta Mininet al controlador POX.

```bash
sudo mn --custom toupe.py --topo toupe,5 --controller remote,ip=localhost,port=6633
```

---

### 4. (Opcional) Levantar Mininet con terminales xterm

Si deseas abrir una terminal xterm para cada host, ejecuta:

```bash
sudo mn --custom toupe.py --topo toupe,5 --controller remote,ip=localhost,port=6633 --xterms
```

---

### 5. Finalizar procesos en el puerto 6633

Si necesitas liberar el puerto 6633 (por ejemplo, si quedó ocupado por una instancia anterior de POX):

```bash
sudo lsof -i :6633
sudo kill -9 <PID>
```s
Reemplaza `<PID>` por el número de proceso que aparece en la salida del primer comando.

---

### 6. Verificar las reglas instaladas en el switch s3

Para ver la tabla de flujos y los puertos del switch s3:

```bash
ovs-ofctl dump-flows s3
ovs-ofctl dump-ports s3
```

---

### 7. Pruebas sugeridas

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
