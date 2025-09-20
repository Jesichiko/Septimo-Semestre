En dispositivos móviles existen diferentes canales de comunicación integrados con alcances y propositos distintos:

## WI-FI
WI-FI es un canal de comunicación **inalambrica** para **distancias largas**. 

Este canal es usado para transmitir información en streams de bits llamados paquetes. Debido a esto, este canal es usado de manera general para transmitir datos entre distancias de cualquier tamaño y esto hace **vulnerable** al canal. Sus vulnerabilidades son:
- **Man in the middle**: Esta vulnerabilidad es la posibilidad de un tercer participante entre una comunicación de cliente y proveedor. Puede existir el caso que una persona esté escuchando la conexión sin que los participantes lo sepan y acceda a **el contenido de los datos compartidos**, pudiendo así **modificar, copiar o incluso eliminar** la información interceptada. Esta es la mayor brecha de seguridad en redes inalambricas y muchas de las brechas de seguridad **nacen a partir de la posibilidad de un tercero en una comunicación**.Para poder prevenir esto existen **protocolos de seguridad** como **TLS** que encripta información intercambiada de un **proveedor a un cliente** (o viceversa) en la capa de TCP o **WPA2/WPA3** que encripta solamente entre un dispositivo local y un punto de acceso (como un router).
- **Sniffing**: Esta vulnerabilidad es también un oyente oculto entre un cliente y un proveedor en una conexión inalambrica, con la única diferencia de que el oyente oculto **solo escucha la conexión y no interviene en ella**. Esto puede ser una amenaza potencial si un canal inalambrico no esta configurada de manera correcta ante ataques como estos ya que posibles terceros pueden robar datos sensibles sin que nunca se sepa de su existencia. 
- **Evil Twin**: Vulnerabilidad en la que un punto de acceso malicioso se hace pasar por uno **legitimo**, tomando así todos los datos que le llegan a el y potencialmente **guardarlos, modificarlos o copiarlos**.
- **MAC Tracking**: En redes locales sin protocolos de seguridad, un tercero puede saber que dispositivo local hizo una petición en concreto dandole seguimiento a su dirección MAC.

## Bluetooth
Bluetooth es un canal de comunicación **inalambrica** usado para **distancias cortas a medias**.

Este canal de comunicación es usado para conexiones no criticas y de corta duración entre dispositivos relativamente cercanos. Usado en mayoria por dispositivos que comparten información de un solo tipo. Para esto, se deben dar permisos a los participantes sobre ciertos datos de cada dispositivo, creando **vulnerabilidades**. Estas son:
- **Bluejacking**:
