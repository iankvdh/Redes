# Redes - Trabajos Prácticos

Este repositorio contiene los trabajos prácticos desarrollados para la materia **Redes (Introducción a los Sistemas Distribuidos)** en la FIUBA. Cada TP se encuentra en su respectiva subcarpeta con su código, documentación y scripts de simulación.

## Contenidos

### TP1 - File Transfer over UDP

Se implementa una aplicación cliente-servidor para la transferencia de archivos sobre una red simulada, utilizando el protocolo UDP con mecanismos de recuperación ante errores. Se desarrollaron dos versiones de protocolo confiable: **Stop & Wait** y **Selective Repeat**, aplicadas tanto a operaciones de **upload** como de **download**. El sistema fue validado con **Mininet** mediante simulaciones de pérdida y fragmentación de paquetes.

• Tecnologías: Python, sockets, Mininet

• Ver carpeta: [`TP1/`](./TP1)

---

### TP2 - Software Defined Networking (SDN)

Se implementa una red definida por software utilizando **Mininet** y el controlador **POX**. Se desarrolló una topología personalizada y un firewall que instala reglas específicas en un switch central para controlar el tráfico. El objetivo fue experimentar con reglas de filtrado y observar su impacto sobre la conectividad entre hosts.

• Tecnologías: Python, POX, OpenFlow, Mininet

• Ver carpeta: [`TP2/`](./TP2)

---

## Autores

| Nombre          | Apellido      | Mail                  | Padrón |
| --------------- | ------------- | --------------------- | ------ |
| Ian             | von der Heyde | ivon@fi.uba.ar        | 107638 |
| Agustín         | Altamirano    | aaltamirano@fi.uba.ar | 110237 |
| Juan Martín     | de la Cruz    | jdelacruz@fi.uba.ar   | 109588 |
| Cristhian David | Noriega       | cnoriega@fi.uba.ar    | 109164 |
| Santiago Tomás  | Fassio        | sfassio@fi.uba.ar     | 109463 |
