import base64
import json
import random
import secrets
import socket
import struct
import sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

archivos = []


class SimpleTLS:
    def __init__(self):
        """TLS 1.3 simplificado usando:
        - Diffie-Hellman para intercambio de claves
        - AEAD (AES-GCM) en lugar de CBC
        - HKDF para derivacion de claves
        """

        # Generamos parametros DH (RFC 3526, grupo 14 - 2048 bits):
        p_hex = "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF"
        p = int(p_hex, 16)
        g = 2

        self.dh_params = dh.DHParameterNumbers(p, g).parameters()

        # Generamos clave privada DH:
        self.dh_private_key = self.dh_params.generate_private_key()
        self.dh_public_key = self.dh_private_key.public_key()

        # Estados de conexion
        self.shared_secret = None
        self.master_secret = None
        self.client_write_key = None
        self.server_write_key = None
        self.client_nonce_base = None
        self.server_nonce_base = None
        self.sequence_number = 0

        # AEAD cipher
        self.aead = None

    def get_dh_public_key_bytes(self) -> bytes:
        # Obtenemos la llave publica DH (efimera) para enviarla:
        return self.dh_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def generar_random_number(self) -> bytes:
        # Se genera un numero entero random de 32 bytes:
        return secrets.token_bytes(32)

    def set_client_dh_public_key(self, client_public_key_pem: bytes):
        # Cargamos la llave publica del cliente:
        client_public_key = serialization.load_pem_public_key(
            client_public_key_pem)

        # Calculamos el secreto compartido usando la llave cargada:
        self.shared_secret = self.dh_private_key.exchange(client_public_key)

    def derive_master_secret(self, client_random: bytes, server_random: bytes):
        # Derivamos llaves con el secreto compartido:

        if not self.shared_secret:
            raise ValueError("No hay secreto compartido DH")

        # Contexto para derivacion
        info = b"TLS 1.3 master secret" + client_random + server_random

        # Derivar master secret usando HKDF
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"", info=info)
        self.master_secret = hkdf.derive(self.shared_secret)
        print(f"Master secret derivado: {self.master_secret.hex()[:32]}...")

    def derive_traffic_keys(self):
        """Derivar claves de tráfico desde el master secret"""
        if not self.master_secret:
            raise ValueError("No hay master secret")

        # Derivar claves para cliente y servidor
        client_hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=b"",
            info=b"TLS 1.3 client write key",
        )
        self.client_write_key = client_hkdf.derive(self.master_secret)

        server_hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=b"",
            info=b"TLS 1.3 server write key",
        )
        self.server_write_key = server_hkdf.derive(
            self.master_secret + b"server")

        # Derivar bases para nonces
        nonce_hkdf_client = HKDF(
            algorithm=hashes.SHA256(),
            length=12,  # GCM nonce size
            salt=b"",
            info=b"TLS 1.3 client nonce",
        )
        self.client_nonce_base = nonce_hkdf_client.derive(
            self.master_secret + b"client_nonce"
        )

        nonce_hkdf_server = HKDF(
            algorithm=hashes.SHA256(),
            length=12,  # GCM nonce size
            salt=b"",
            info=b"TLS 1.3 server nonce",
        )
        self.server_nonce_base = nonce_hkdf_server.derive(
            self.master_secret + b"server_nonce"
        )

        # Inicializar AEAD con clave del servidor
        self.aead = AESGCM(self.server_write_key)

        print("Claves de tráfico derivadas exitosamente")

    def construct_nonce(self, sequence_num: int, is_client: bool = False) -> bytes:
        """Construir nonce para AEAD usando número de secuencia"""
        base = self.client_nonce_base if is_client else self.server_nonce_base

        # XOR con número de secuencia (últimos 8 bytes del nonce)
        nonce = bytearray(base)
        seq_bytes = sequence_num.to_bytes(8, "big")

        # XOR los últimos 8 bytes
        for i in range(8):
            nonce[4 + i] ^= seq_bytes[i]

        return bytes(nonce)

    def aead_encrypt(self, plaintext: str, sequence_num: int) -> bytes:
        """Encriptar con AEAD (AES-GCM)"""
        if not self.aead:
            raise ValueError("AEAD no inicializado")

        nonce = self.construct_nonce(sequence_num, is_client=False)
        data = plaintext.encode("utf-8")

        # AEAD proporciona confidencialidad + autenticación
        ciphertext = self.aead.encrypt(nonce, data, None)

        # Retornar nonce + ciphertext (el nonce puede ser público)
        return nonce + ciphertext

    def aead_decrypt(
        self, encrypted_data: bytes, sequence_num: int, is_client: bool = True
    ) -> str:
        """Desencriptar con AEAD (AES-GCM)"""
        if len(encrypted_data) < 12:
            raise ValueError("Datos encriptados demasiado cortos")

        # Extraer nonce y ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        # Usar clave del cliente para desencriptar
        client_aead = AESGCM(self.client_write_key)

        try:
            plaintext = client_aead.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Fallo en autenticación AEAD: {e}")


class TCP:
    def __init__(self, puerto_raiz: int, buffer: int, socket: socket.socket):
        self.informacion_server = {
            "header": {
                "puerto_raiz": puerto_raiz,
                "puerto_destino": 0,
                "secuencia_propia": 0,
                "secuencia_ACK": 0,
                "data_offset": 20,
                "window_size": buffer,
                "flags": {"SYN": 0, "ACK": 0, "FIN": 0},
                "padding": 0,
            },
        }
        self.sock = socket
        self.addr_destino = None
        self.tls = SimpleTLS()  # Nueva implementación TLS
        self.client_random = None
        self.server_random = None

        if not self.sock:
            raise ValueError("Error, el socket no fue creado")

    def parsear_mensaje(self, data: bytes) -> dict:
        if len(data) < 20:
            return None

        header = struct.unpack("!HHIIBBHHH", data[:20])
        parsed_data = {
            "header": {
                "puerto_raiz": header[0],
                "puerto_destino": header[1],
                "secuencia_propia": header[2],
                "secuencia_ACK": header[3],
                "data_offset": (header[4] >> 4) * 4,
                "flags": {
                    "SYN": (header[5] >> 1) & 1,
                    "ACK": header[5] & 1,
                    "FIN": (header[5] >> 2) & 1,
                },
                "window_size": header[6],
            },
            "payload": data[20:] if len(data) > 20 else b"",
        }
        return parsed_data

    def header_a_bytes(self) -> bytes:
        flags_byte = (
            (self.informacion_server["header"]["flags"]["FIN"] << 2)
            | (self.informacion_server["header"]["flags"]["SYN"] << 1)
            | self.informacion_server["header"]["flags"]["ACK"]
        )

        return struct.pack(
            "!HHIIBBHHH",
            self.informacion_server["header"]["puerto_raiz"],
            self.informacion_server["header"]["puerto_destino"],
            self.informacion_server["header"]["secuencia_propia"],
            self.informacion_server["header"]["secuencia_ACK"],
            (self.informacion_server["header"]["data_offset"] // 4) << 4,
            flags_byte,
            self.informacion_server["header"]["window_size"],
            0,
            0,
        )

    def recibir_handshake(self) -> tuple[dict, tuple]:
        data, addr = self.sock.recvfrom(
            self.informacion_server["header"]["window_size"]
        )
        data_parseada = self.parsear_mensaje(data)
        return data_parseada, addr

    def threeway_handshake(self, seq_inicial: int) -> bool:
        self.informacion_server["header"]["secuencia_propia"] = seq_inicial

        # 1. Recibir SYN
        data, addr = self.recibir_handshake()
        if not data or data["header"]["flags"]["SYN"] != 1:
            print("Error: SYN inválido recibido")
            return False

        self.addr_destino = addr
        self.informacion_server["header"]["puerto_destino"] = data["header"][
            "puerto_raiz"
        ]
        seq_cliente = data["header"]["secuencia_propia"]
        self.informacion_server["header"]["secuencia_ACK"] = seq_cliente + 1
        print(f"SYN recibido del cliente - Seq cliente: {seq_cliente}")

        # 2. Enviar SYN-ACK
        self.informacion_server["header"]["flags"]["ACK"] = 1
        self.informacion_server["header"]["flags"]["SYN"] = 1
        self.informacion_server["header"]["secuencia_propia"] += 1

        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes, self.addr_destino)
        print(
            f"SYN-ACK enviado - Seq servidor: {
                self.informacion_server['header']['secuencia_propia']}"
        )

        # Reset flags
        self.informacion_server["header"]["flags"] = {
            key: 0 for key in self.informacion_server["header"]["flags"]
        }

        # 3. Recibir ACK final
        data, addr = self.recibir_handshake()
        if not data or data["header"]["flags"]["ACK"] != 1:
            print("Error: ACK final inválido")
            return False

        ack_recibido = data["header"]["secuencia_ACK"]
        if ack_recibido != self.informacion_server["header"]["secuencia_propia"] + 1:
            print(
                f"Error: ACK incorrecto. Esperado: {
                    self.informacion_server['header']['secuencia_propia'] + 1}, Recibido: {ack_recibido}"
            )
            return False

        self.informacion_server["header"]["secuencia_propia"] += 1
        self.informacion_server["header"]["secuencia_ACK"] = (
            data["header"]["secuencia_propia"] + 1
        )
        print("ACK final recibido correctamente - Handshake TCP completado")
        return True

    def tls_handshake(self) -> bool:
        """TLS 1.3 simplificado con Diffie-Hellman + AEAD"""
        print("Iniciando handshake TLS 1.3...")

        try:
            # 1. Generar números aleatorios
            self.server_random = self.tls.generar_random_number()

            # 2. Enviar ServerHello con clave pública DH
            dh_public_key_pem = self.tls.get_dh_public_key_bytes()
            mensaje_server_hello = {
                "type": "server_hello",
                "server_random": base64.b64encode(self.server_random).decode("utf-8"),
                "dh_public_key": base64.b64encode(dh_public_key_pem).decode("utf-8"),
                "cipher_suite": "AEAD-AES256-GCM-SHA256",  # TLS 1.3 suite
            }

            self.enviar_sin_cifrar(json.dumps(mensaje_server_hello))
            print("ServerHello con clave DH enviado")

            # 3. Recibir ClientHello con clave DH del cliente
            data, addr = self.recibir_de_sin_cifrar()
            if not data:
                print("Error: No se recibió ClientHello")
                return False

            mensaje_cliente = json.loads(data["payload"].decode("utf-8"))
            if mensaje_cliente.get("type") != "client_hello":
                print("Error: ClientHello inválido")
                return False

            # Extraer datos del cliente
            self.client_random = base64.b64decode(
                mensaje_cliente["client_random"])
            client_dh_public_key = base64.b64decode(
                mensaje_cliente["dh_public_key"])

            print("ClientHello recibido")

            # 4. Calcular secreto compartido y derivar claves
            self.tls.set_client_dh_public_key(client_dh_public_key)
            self.tls.derive_master_secret(
                self.client_random, self.server_random)
            self.tls.derive_traffic_keys()

            # 5. Enviar confirmación (ya encriptada)
            confirmacion = {"type": "handshake_finished", "status": "success"}
            self.enviar_cifrado(json.dumps(confirmacion))
            print("Handshake TLS 1.3 completado exitosamente")
            return True

        except Exception as e:
            print(f"Error en handshake TLS: {e}")
            return False

    def enviar_sin_cifrar(self, data: str):
        data_en_bytes = data.encode("utf-8")
        self.informacion_server["header"]["secuencia_propia"] += 1
        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes + data_en_bytes, self.addr_destino)
        self.informacion_server["header"]["flags"] = {
            key: 0 for key in self.informacion_server["header"]["flags"]
        }

    def recibir_de_sin_cifrar(self) -> tuple[dict, tuple]:
        data, addr = self.sock.recvfrom(
            self.informacion_server["header"]["window_size"]
        )
        data_parseada = self.parsear_mensaje(data)
        if not data_parseada:
            return None, None
        return data_parseada, addr

    def enviar_cifrado(self, data: str):
        """Enviar datos con AEAD (confidencialidad + autenticación)"""
        # Usar número de secuencia como contador para nonce
        data_cifrada = self.tls.aead_encrypt(data, self.tls.sequence_number)
        self.tls.sequence_number += 1

        self.informacion_server["header"]["secuencia_propia"] += 1
        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes + data_cifrada, self.addr_destino)

        print(
            f"Datos AEAD enviados - Seq: {
                self.informacion_server['header']['secuencia_propia']}"
        )
        self.informacion_server["header"]["flags"] = {
            key: 0 for key in self.informacion_server["header"]["flags"]
        }

    def recibir_cifrado(self) -> tuple[dict, tuple]:
        data, addr = self.sock.recvfrom(
            self.informacion_server["header"]["window_size"]
        )
        data_parseada = self.parsear_mensaje(data)

        if not data_parseada:
            return None, None

        # Verificar ACK
        ack_recibido = data_parseada["header"]["secuencia_ACK"]
        if ack_recibido != self.informacion_server["header"]["secuencia_propia"] + 1:
            print(
                f"ACK incorrecto: esperado {
                    self.informacion_server['header']['secuencia_propia'] + 1}, recibido {ack_recibido}"
            )
            return None, None

        print(f"ACK correcto recibido: {ack_recibido}")
        return data_parseada, addr

    def enviar_archivo(self, archivo_texto: list) -> bool:
        print(f"Iniciando envío AEAD de {len(archivo_texto)} líneas...")

        for i, linea in enumerate(archivo_texto):
            if not linea.strip():
                continue

            try:
                mensaje = f"{i}:{linea}"
                self.enviar_cifrado(mensaje)

                self.sock.settimeout(5.0)
                data, addr = self.recibir_cifrado()
                self.sock.settimeout(None)

                if not data:
                    print(f"Error: No se recibió ACK para línea {i+1}")
                    return False

                print(f"Línea {i+1} enviada y confirmada (AEAD)")

            except socket.timeout:
                print(f"Error: Timeout esperando ACK para línea {i+1}")
                return False
            except Exception as e:
                print(f"Error: No se pudo enviar la línea {i+1}: {e}")
                return False

        # Enviar FIN
        self.informacion_server["header"]["flags"]["FIN"] = 1
        self.informacion_server["header"]["secuencia_propia"] += 1
        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes, self.addr_destino)

        print("Mensaje FIN enviado")
        print("Transmisión de archivo completada (con TLS 1.3 + AEAD)")
        return True


def leer_archivo(nombre_archivo: str):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as texto:
            archivos.append(texto.read().split("\n"))
        return True
    except Exception:
        return False


def main():
    UDP_IP = "127.0.0.1"
    pool_seqs = list(range(20000, 40000))
    UDP_PORT = 20000
    num_archivos = 0

    if len(sys.argv) < 2:
        print("Debes ingresar servidor.py <archivo1> <archivo2> ...")
        exit(1)

    # Lectura archivos
    for archivo_a_leer in sys.argv[1:]:
        if leer_archivo(archivo_a_leer):
            num_archivos += 1
        else:
            print(f'No se pudo leer el archivo "{archivo_a_leer}"')

    if num_archivos == 0:
        print("Error: No se pudieron leer archivos válidos")
        exit(1)
    print(f"Total de archivos leídos = {num_archivos}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
    except socket.error as e:
        print(f"Error: {e} al crear socket, finalizando servidor...")
        exit(1)
    print(f"Servidor escuchando en {UDP_IP}:{UDP_PORT}...")

    try:
        while True:
            if not pool_seqs:
                pool_seqs = list(range(20000, 40000))

            seq_server = random.choice(pool_seqs)
            pool_seqs.remove(seq_server)
            print(
                f"\nEsperando nueva conexion... (SEQ inicial del servidor: {
                    seq_server})"
            )

            tcp_server = TCP(UDP_PORT, 1024, sock)

            # 1. Handshake TCP
            if tcp_server.threeway_handshake(seq_server):
                print("Conexion TCP establecida exitosamente")

                # 2. Handshake TLS 1.3
                if tcp_server.tls_handshake():
                    print("Conexion TLS 1.3 establecida exitosamente")

                    # 3. Envío de archivo con AEAD
                    archivo_seleccionado = random.choice(archivos)
                    print("Archivo seleccionado para envío AEAD")
                    if tcp_server.enviar_archivo(archivo_seleccionado):
                        print("Transmision AEAD exitosa")
                    else:
                        print("Error en transmision AEAD")
                else:
                    print("Error en handshake TLS 1.3")
            else:
                print("Error en handshake TCP, esperando otro cliente...")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
