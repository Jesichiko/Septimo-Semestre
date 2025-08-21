import random
import socket


def codificar_utf(secuencia_str) -> bytes:
    return str(secuencia_str).encode("utf-8")


def enviar_mensaje(socket: socket.socket, secuencia_bytes: bytes, addr):
    socket.sendto(secuencia_bytes, addr)
    return


def recibir_mensaje(socket: socket.socket, tam_buffer: int):
    data, addr = socket.recvfrom(tam_buffer)
    return data, addr


def is_mensaje_siguiente(seq_anterior: int, seq_recibido: int) -> bool:
    return seq_recibido == seq_anterior + 1


def recibir_archivo(sock, mi_seq, seq_esperada_servidor, servidor_addr):
    while True:
        try:
            # Recibimos mensaje del servidor
            data, addr = sock.recvfrom(1024)
            mensaje = data.decode("utf-8").split("\n")

            # Verificamos si es mensaje FIN:
            if len(mensaje) >= 2 and mensaje[-1] == "FIN":
                print("Archivo recibido completamente")
                break

            if len(mensaje) >= 2:
                seq_recibida = int(mensaje[0])
                linea_texto = mensaje[1]

                # Verificamos la secuencia correcta:
                if seq_recibida == seq_esperada_servidor:
                    print(linea_texto)

                    # Enviar ACK con la siguiente secuencia esperada:
                    ack_msg = f"{seq_recibida + 1}\nACK"
                    sock.sendto(ack_msg.encode("utf-8"), servidor_addr)

                    seq_esperada_servidor += 1
                else:
                    print(
                        f"Secuencia incorrecta: esperaba {
                            seq_esperada_servidor}, recibí {seq_recibida}"
                    )
                    # Reenviamos ACK con la secuencia correcta esperada:
                    ack_msg = f"{seq_esperada_servidor}\nNACK"
                    sock.sendto(ack_msg.encode("utf-8"), servidor_addr)

        except Exception as e:
            print(f"Error recibiendo datos: {e}")
            break


def handshake_cliente(sock, mi_seq, servidor_addr):
    try:
        print(f"Iniciando handshake con secuencia inicial: {mi_seq}")

        # 1. Enviar SYN
        syn_mensaje = f"{mi_seq}\nSYN"
        sock.sendto(codificar_utf(syn_mensaje), servidor_addr)
        print(f"SYN enviado con secuencia {mi_seq}")

        # 2. Recibir SYN-ACK
        data, addr = sock.recvfrom(1024)

        if addr != servidor_addr:
            print("Error: SYN-ACK recibido de direccion incorrecta")
            return None

        syn_ack_datos = data.decode("utf-8").split("\n")

        if len(syn_ack_datos) >= 3 and syn_ack_datos[-1] == "SYN-ACK":
            seq_servidor = int(syn_ack_datos[0])
            ack_esperado = int(syn_ack_datos[1])

            print(
                f"SYN-ACK recibido - Seq servidor: {
                    seq_servidor}, ACK esperado: {ack_esperado}"
            )

            # Verificar que el ACK sea correcto
            if ack_esperado == mi_seq + 1:
                # 3. Enviar ACK final
                ack_final = f"{mi_seq + 1}\n{seq_servidor + 1}\nACK"
                sock.sendto(ack_final.encode("utf-8"), servidor_addr)
                print(
                    f"ACK final enviado - Mi seq: {mi_seq +
                                                   1}, ACK servidor: {seq_servidor + 1}"
                )

                # Retornar la próxima secuencia esperada del servidor
                return seq_servidor + 1
            else:
                print(
                    f"Error: ACK incorrecto en SYN-ACK. Esperado: {
                        mi_seq + 1}, Recibido: {ack_esperado}"
                )
        else:
            print("Error: Mensaje SYN-ACK malformado")

    except Exception as e:
        print(f"Error durante handshake: {e}")

    return None


def main():
    print("=== Cliente UDP iniciado ===")

    # Configurar socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(10.0)  # Timeout de 10 segundos

    # Generar secuencia inicial aleatoria
    mi_seq = random.randint(20000, 30000)
    addr_server = ("127.0.0.1", 20000)

    print(f"Conectando al servidor en {addr_server[0]}:{addr_server[1]}")

    try:
        # Realizar handshake
        seq_servidor = handshake_cliente(sock, mi_seq, addr_server)

        if seq_servidor is not None:
            print("Handshake exitoso")
            recibir_archivo(sock, mi_seq + 1, seq_servidor, addr_server)
        else:
            print("Error: No se pudo completar el handshake")

    except Exception as e:
        print(f"Error en cliente: {e}")
    finally:
        sock.close()
        print("Cliente desconectandose...")


if __name__ == "__main__":
    main()
