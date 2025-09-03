import json
import socket
import sys


def crear_mensaje(nombre_archivo: str) -> bytes:
    peticion = {
        "operacion": "peticion",
        "archivo": nombre_archivo,
    }
    return json.dumps(peticion).encode("utf-8")


def respuesta_server(response: bytes) -> bool:
    try:
        respuesta = json.loads(response.decode("utf-8"))
        # El servidor responde con "operacion": "respuesta", no "peticion"
        return (
            respuesta.get("operacion") == "respuesta"
            and respuesta.get("respuesta") == "ACK"
        )
    except json.JSONDecodeError as e:
        print(f"Error decodificando respuesta del servidor: {e}")
        return False
    except Exception as e:
        print(f"Error procesando respuesta: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Uso: python cliente.py nombre_archivo")
        exit(-1)

    nombre_archivo = sys.argv[1]
    SERVER_IP = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
    SERVER_PORT = int(sys.argv[3]) if len(sys.argv) > 3 else 50000

    try:
        # 1. Creamos el socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(10.0)  # Timeout de 10 segundos

        # 2. Enviamos peticion al servidor
        mensaje = crear_mensaje(nombre_archivo)
        sock.sendto(mensaje, (SERVER_IP, SERVER_PORT))
        print(f"Peticion enviada para el archivo: {nombre_archivo}")

        # 3. Recibimos respuesta del servidor
        data, addr = sock.recvfrom(1024)
        print(f"Respuesta recibida del servidor {addr}")

        # 4. Procesamos la respuesta
        if respuesta_server(data):
            print(f"El archivo '{nombre_archivo}' SI existe en el servidor")
        else:
            print(f"El archivo '{nombre_archivo}' NO existe en el servidor")
            respuesta_json = json.loads(data.decode("utf-8"))
            if "motivo" in respuesta_json:
                print(f"Motivo: {respuesta_json['motivo']}")
            print(f"Respuesta completa: {respuesta_json}")

    except socket.timeout:
        print("Error: Timeout - El servidor no respondio en 10 segundos")
    except socket.error as e:
        print(f"Error de socket: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
