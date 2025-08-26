import random
import socket
import sys

archivos = []


def leer_archivo(nombre_archivo: str):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as texto:
            archivos.append(texto.read().split("\n"))
        return True
    except Exception:
        return False


def codificar_utf(secuencia_str) -> bytes:
    return str(secuencia_str).encode("utf-8")


def enviar_mensaje(socket: socket.socket, secuencia_bytes: bytes, addr):
    socket.sendto(secuencia_bytes, addr)
    return


def recibir_mensaje(socket: socket.socket, tam_buffer: int):
    data, addr = socket.recvfrom(tam_buffer)
    return data, addr


def incrementar_secuencia(seq_actual: int) -> int:
    return seq_actual + 1


def is_mensaje_siguiente(seq_anterior: int, seq_recibido: int) -> bool:
    return seq_recibido == seq_anterior + 1


def threeway_handshake(socket: socket.socket, seq_server: int) -> tuple:
    buffer = 1024

    # En cada mensaje enviamos:
    # Sequencia_propia\n
    # Sequencia_del_otro +1
    # Banderas (ACK, SYN)
    try:

        # 1. Recibir SYN del cliente
        data, addr = recibir_mensaje(socket, buffer)
        datos = data.decode("utf-8").split("\n")

        if len(datos) < 2 or datos[-1] != "SYN":
            print("Error: Mensaje SYN no valido recibido")
            return None, None

        seq_cliente = int(datos[0])
        print(f"SYN recibido del cliente {addr} con secuencia {seq_cliente}")

        # 2. Enviar SYN-ACK al cliente
        syn_ack_mensaje = f"{seq_server}\n{seq_cliente + 1}\nSYN-ACK"
        enviar_mensaje(socket, codificar_utf(syn_ack_mensaje), addr)
        print(f"SYN-ACK enviado con secuencia del servidor {seq_server}")

        # 3. Recibir ACK final del cliente
        data, addr_final = recibir_mensaje(socket, buffer)
        datos_finales = data.decode("utf-8").split("\n")

        if len(datos_finales) < 3 or datos_finales[-1] != "ACK":
            print("Error: ACK final no valido, finalizando conexion")
            return None, None

        seq_cliente_final = int(datos_finales[0])
        ack_servidor = int(datos_finales[1])
        if not is_mensaje_siguiente(seq_server, ack_servidor):
            print(
                f"Error: ACK esperado {
                    seq_server + 1}, recibido {ack_servidor}"
            )

        if addr != addr_final:
            print("Error: Direccion del cliente cambio durante handshake")
            return None, None

        print("Three-way handshake completado exitosamente")
        return seq_cliente_final, addr

    except Exception as e:
        print(f"Error inesperado durante handshake: {e}")
        return None, None


def enviar_texto(
    archivo_texto: list, sock: socket.socket, seq_server: int, seq_cliente: int, addr
):
    buffer = 1024
    seq_actual = seq_server

    print(f"Iniciando envio de {len(archivo_texto)} lineas a {addr}...")

    for i, linea in enumerate(archivo_texto):

        # Saltamos lineas vacias:
        if not linea.strip():
            continue

        try:
            # Enviamos linea con numero de seq:
            mensaje = f"{seq_actual}\n{i}:{linea}"
            enviar_mensaje(sock, codificar_utf(mensaje), addr)

            # Esperamos ACK de que le llego al cliente con un timeout:
            sock.settimeout(5.0)  # 5 segundos de timeout
            data, addr_respuesta = recibir_mensaje(sock, buffer)
            sock.settimeout(None)

            if addr_respuesta != addr:
                print("Error: ACK recibido de direccion incorrecta")
                return False

            # Verificamos el ACK del cliente:
            ack_datos = data.decode("utf-8").split("\n")
            ack_recibido = int(ack_datos[0])

            if not is_mensaje_siguiente(seq_actual, ack_recibido):
                print(
                    f"Error: ACK esperado {
                        seq_actual + 1}, recibido {ack_recibido}"
                )
                return False
            seq_actual = incrementar_secuencia(seq_actual)

        except socket.timeout:
            print(f"Error: Timeout esperando ACK para linea {i+1}")
            return False
        except Exception as e:
            print(f"Error: No se pudo enviar la linea {i+1}: {e}")
            return False

    # Enviamos mensaje de fin de transmision:
    fin_mensaje = f"{seq_actual}\nFIN"
    enviar_mensaje(sock, codificar_utf(fin_mensaje), addr)
    print("Transmision de archivo completada")
    return True


def main():
    UDP_IP = "127.0.0.1"  # Localhost para pruebas
    seq_server = 20000
    UDP_PORT = 20000
    num_archivos = 0

    # Entrada del servidor (archivos.txt)
    if len(sys.argv) < 3:
        print("Debes ingresar servidor.py <archivo1> <archivo2> <archivo3> ...")
        exit(1)

    # Lectura archivos
    for archivo_a_leer in sys.argv[1:]:
        if leer_archivo(archivo_a_leer):
            num_archivos += 1
        else:
            print(f'No se pudo leer el archivo "{archivo_a_leer}"')
    if num_archivos == 0:
        print("Error: No se pudieron leer archivos validos")
        exit(1)
    print(f"Total de archivos leidos = {num_archivos}")

    # Configuracion del socket UDP
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
    except socket.error as e:
        print(f"Error: {e} al crear socket, finalizando servidor...")
        exit(1)
    print(f"Servidor escuchando en {UDP_IP}:{UDP_PORT}...")

    try:
        while True:

            # Seleccionamos un numero del pool y lo eliminamos
            # para una conexion con un cliente i dado:
            print(
                f"\nEsperando nueva conexion con un cliente ... (SEQ inicial del servidor: {
                    seq_server})"
            )

            # Ejecutamos el threeway_handshake del cliente i dado:
            seq_cliente, addr = threeway_handshake(sock, seq_server)
            if seq_cliente is None:
                print(
                    "Error: Se intento una conexion con un cliente pero fallo, esperando otro cliente..."
                )
                continue

            # Seleccionamos un archivo aleatorio para enviarlo al cliente i:
            if archivos:
                archivo_seleccionado = random.choice(archivos)
                archivos.remove(archivo_seleccionado)
                print(f"Archivo seleccionado para envio al cliente con {addr}")

                if enviar_texto(
                    archivo_seleccionado, sock, seq_server + 1, seq_cliente, addr
                ):
                    print(f"Transmision del texto exitosa a {addr}")
                else:
                    print(f"Error: No se pudo enviar el texto a {addr}")
            else:
                print(
                    "Error: Ya no hay archivos disponibles para enviar, terminando conexiones"
                )
                socket.close()
                exit(-1)

    except Exception as e:
        print(f"Error inesperado en servidor: {e}")
    finally:
        sock.close()
        print("Socket cerrado")


if __name__ == "__main__":
    main()


"""
TO DO:
    1. CRC
    2. Checksums
    3. Pool de seqs por parte del sorted
    4. Hilos
"""
