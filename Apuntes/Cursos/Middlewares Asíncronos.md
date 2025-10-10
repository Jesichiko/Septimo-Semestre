Existen varios middlewares para manejar peticiones de manera asincrona:

## Remote Procedure Call (RPC):
Una de las principales formas de comunicación de los sistemas distribuidos en el **intercambio explícito de mensajes entre procesos**, sin embargo, **las operaciones de enviar y recibir no ocultan la comunicación** en absoluto, lo cual es importante para lograr la transparencia de acceso en sistemas distribuidos.

Cuando un proceso en una máquina local llama a un **proceso remoto** este crea **una copia temporal solo de la cabecera (nombre) del proceso** que tiene la responsabilidad de **enviar un mensaje al servidor con dicho proceso, esperar una respuesta y devolverla.** Para esto se crea un **stub**, donde cada participante "ve" la misma variable (una donde se retorna el resultado del mensaje, otra donde se da el resultado del proceso).r
## Remote Method Invocation (RMI)


## NET Remoting (.NET)

