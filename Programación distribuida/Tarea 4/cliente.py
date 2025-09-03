import base64
import json
import random
import secrets
import socket
import struct

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


class SimpleTLSCliente:
    def __init__(self):
        """TLS 1.3 cliente con Diffie-Hellman + AEAD"""

        # Parámetros DH (mismo grupo que el servidor)
        p_hex = "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF"
        p = int(p_hex, 16)
        g = 2

        self.dh_params = dh.DHParameterNumbers(p, g).parameters()

        # Generar par de claves DH del cliente
        self.dh_private_key = self.dh_params.generate_private_key()
        self.dh_public_key = self.dh_private_key.public_key()

        # Estados de conexión
        self.shared_secret = None
        self.master_secret = None
        self.client_write_key = None
        self.server_write_key = None
        self.client_nonce_base = None
        self.server_nonce_base = None
        self.sequence_number = 0

        # AEAD ciphers
        self.client_aead = None
        self.server_aead = None

    def get_dh_public_key_bytes(self) -> bytes:
        """Obtener clave pública DH del cliente"""
        return self.dh_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def generar_numero_aleatorio(self) -> bytes:
        """Generar 32 bytes aleatorios"""
        return secrets.token_bytes(32)

    def set_server_dh_public_key(self, server_public_key_pem: bytes):
        """Procesar clave pública del servidor y calcular secreto compartido"""
        server_public_key = serialization.load_pem_public_key(
            server_public_key_pem)

        # Calcular secreto compartido
        self.shared_secret = self.dh_private_key.exchange(server_public_key)

    def derive_master_secret(self, client_random: bytes, server_random: bytes):
        """Derivar master secret (igual que en servidor)"""
        if not self.shared_secret:
            raise ValueError("No hay secreto compartido DH")

        info = b"TLS 1.3 master secret" + client_random + server_random

        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=b"", info=info)
        self.master_secret = hkdf.derive(self.shared_secret)
        print(f"Master secret derivado: {self.master_secret.hex()[:32]}...")

    def derive_traffic_keys(self):
        """Derivar claves de tráfico (misma lógica que servidor)"""
        if not self.master_secret:
            raise ValueError("No hay master secret")

        # Claves simétricas (mismas que el servidor)
        client_hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"",
            info=b"TLS 1.3 client write key",
        )
        self.client_write_key = client_hkdf.derive(self.master_secret)

        server_hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"",
            info=b"TLS 1.3 server write key",
        )
        self.server_write_key = server_hkdf.derive(
            self.master_secret + b"server")

        # Nonces bases
        nonce_hkdf_client = HKDF(
            algorithm=hashes.SHA256(), length=12, salt=b"", info=b"TLS 1.3 client nonce"
        )
        self.client_nonce_base = nonce_hkdf_client.derive(
            self.master_secret + b"client_nonce"
        )

        nonce_hkdf_server = HKDF(
            algorithm=hashes.SHA256(), length=12, salt=b"", info=b"TLS 1.3 server nonce"
        )
        self.server_nonce_base = nonce_hkdf_server.derive(
            self.master_secret + b"server_nonce"
        )

        # Inicializar AEAD ciphers
        self.client_aead = AESGCM(self.client_write_key)
        self.server_aead = AESGCM(self.server_write_key)

        print("Claves de tráfico derivadas exitosamente (cliente)")

    def construct_nonce(self, sequence_num: int, is_client: bool = True) -> bytes:
        """Construir nonce para AEAD"""
        base = self.client_nonce_base if is_client else self.server_nonce_base

        nonce = bytearray(base)
        seq_bytes = sequence_num.to_bytes(8, "big")

        for i in range(8):
            nonce[4 + i] ^= seq_bytes[i]

        return bytes(nonce)

    def encrypt_data(self, plaintext: str, sequence_num: int) -> bytes:
        """Encriptar con AEAD usando clave del cliente"""
        if not self.client_aead:
            raise ValueError("AEAD del cliente no inicializado")

        nonce = self.construct_nonce(sequence_num, is_client=True)
        data = plaintext.encode("utf-8")

        ciphertext = self.client_aead.encrypt(nonce, data, None)
        return nonce + ciphertext

    def decrypt_data(self, encrypted_data: bytes, sequence_num: int) -> str:
        """Desencriptar datos del servidor con AEAD"""
        if len(encrypted_data) < 12:
            raise ValueError("Datos encriptados demasiado cortos")

        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        if not self.server_aead:
            raise ValueError("AEAD del servidor no inicializado")

        try:
            plaintext = self.server_aead.decrypt(nonce, ciphertext, None)
            return plaintext.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Fallo en autenticación AEAD: {e}")


class TCPCliente:
    def __init__(self, buffer: int):
        self.informacion_cliente = {
            "header": {
                "puerto_raiz": 0,
                "puerto_destino": 0,
                "secuencia_propia": 0,
                "secuencia_ACK": 0,
                "data_offset": 20,
                "window_size": buffer,
                "flags": {"SYN": 0, "ACK": 0, "FIN": 0},
                "padding": 0,
            },
            "data": None,
        }
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr_servidor = None
        self.tls = SimpleTLSCliente()
        self.client_random = None
        self.server_random = None

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
                "padding": 0,
            },
            "payload": data[20:] if len(data) > 20 else b"",
            "data": (
                data[20:].decode(
                    "utf-8", errors="ignore") if len(data) > 20 else ""
            ),
        }
        return parsed_data

    def header_a_bytes(self) -> bytes:
        flags_byte = (
            (self.informacion_cliente["header"]["flags"]["FIN"] << 2)
            | (self.informacion_cliente["header"]["flags"]["SYN"] << 1)
            | self.informacion_cliente["header"]["flags"]["ACK"]
        )

        return struct.pack(
            "!HHIIBBHHH",
            self.informacion_cliente["header"]["puerto_raiz"],
            self.informacion_cliente["header"]["puerto_destino"],
            self.informacion_cliente["header"]["secuencia_propia"],
            self.informacion_cliente["header"]["secuencia_ACK"],
            (self.informacion_cliente["header"]["data_offset"] // 4) << 4,
            flags_byte,
            self.informacion_cliente["header"]["window_size"],
            0,
            0,
        )

    def enviar_sin_cifrar(self, data: str):
        """Enviar datos sin cifrar (para handshake)"""
        data_en_bytes = data.encode("utf-8")

        if not (
            self.informacion_cliente["header"]["flags"]["SYN"]
            and not self.informacion_cliente["header"]["flags"]["ACK"]
        ):
            self.informacion_cliente["header"]["secuencia_propia"] += 1

        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes + data_en_bytes, self.addr_servidor)

        print(
            f"Mensaje sin cifrar enviado - Seq: {
                self.informacion_cliente['header']['secuencia_propia']}"
        )
        self.informacion_cliente["header"]["flags"] = {
            key: 0 for key in self.informacion_cliente["header"]["flags"]
        }

    def enviar_cifrado(self, data: str):
        """Enviar datos cifrados con AEAD"""
        data_cifrada = self.tls.encrypt_data(data, self.tls.sequence_number)
        self.tls.sequence_number += 1

        self.informacion_cliente["header"]["secuencia_propia"] += 1
        header_en_bytes = self.header_a_bytes()
        self.sock.sendto(header_en_bytes + data_cifrada, self.addr_servidor)

        print(
            f"ACK AEAD enviado - Seq: {
                self.informacion_cliente['header']['secuencia_propia']}"
        )
        self.informacion_cliente["header"]["flags"] = {
            key: 0 for key in self.informacion_cliente["header"]["flags"]
        }

    def recibir_de(self) -> tuple[dict, tuple]:
        data, addr = self.sock.recvfrom(
            self.informacion_cliente["header"]["window_size"]
        )
        data_parseada = self.parsear_mensaje(data)
        if not data_parseada:
            return None, None
        return data_parseada, addr

    def handshake_cliente(self, mi_seq: int, servidor_addr: tuple) -> bool:
        """Handshake TCP de 3 vías"""
        self.addr_servidor = servidor_addr
        self.informacion_cliente["header"]["secuencia_propia"] = mi_seq
        self.informacion_cliente["header"]["puerto_raiz"] = self.sock.getsockname()[
            1]
        self.informacion_cliente["header"]["puerto_destino"] = servidor_addr[1]

        try:
            print(f"Iniciando handshake TCP con secuencia inicial: {mi_seq}")

            # 1. Enviar SYN
            self.informacion_cliente["header"]["flags"]["SYN"] = 1
            header_en_bytes = self.header_a_bytes()
            self.sock.sendto(header_en_bytes, self.addr_servidor)
            self.informacion_cliente["header"]["flags"] = {
                key: 0 for key in self.informacion_cliente["header"]["flags"]
            }
            print(f"SYN enviado con secuencia {mi_seq}")

            # 2. Recibir SYN-ACK
            data, addr = self.recibir_de()
            if not data or addr != servidor_addr:
                print("Error: SYN-ACK no válido")
                return False

            if (
                data["header"]["flags"]["SYN"] == 1
                and data["header"]["flags"]["ACK"] == 1
            ):
                seq_servidor = data["header"]["secuencia_propia"]
                ack_esperado = data["header"]["secuencia_ACK"]
                print(
                    f"SYN-ACK recibido - Seq servidor: {
                        seq_servidor}, ACK esperado: {ack_esperado}"
                )

                if ack_esperado == mi_seq + 1:
                    # 3. Enviar ACK final
                    self.informacion_cliente["header"]["secuencia_ACK"] = (
                        seq_servidor + 1
                    )
                    self.informacion_cliente["header"]["secuencia_propia"] += 1
                    self.informacion_cliente["header"]["flags"]["ACK"] = 1

                    header_en_bytes = self.header_a_bytes()
                    self.sock.sendto(header_en_bytes, self.addr_servidor)
                    self.informacion_cliente["header"]["flags"] = {
                        key: 0 for key in self.informacion_cliente["header"]["flags"]
                    }

                    print(f"ACK final enviado - Handshake TCP completado")
                    return True
                else:
                    print(f"Error: ACK incorrecto en SYN-ACK")
            else:
                print("Error: Mensaje SYN-ACK malformado")

        except Exception as e:
            print(f"Error durante handshake TCP: {e}")
        return False

    def tls_handshake_cliente(self) -> bool:
        """Handshake TLS 1.3 del cliente"""
        print("Iniciando handshake TLS 1.3 del cliente...")

        try:
            # 1. Generar Client Random y preparar ClientHello
            self.client_random = self.tls.generar_numero_aleatorio()
            client_dh_public_key = self.tls.get_dh_public_key_bytes()

            mensaje_client_hello = {
                "type": "client_hello",
                "client_random": base64.b64encode(self.client_random).decode("utf-8"),
                "dh_public_key": base64.b64encode(client_dh_public_key).decode("utf-8"),
                "supported_cipher_suites": ["AEAD-AES256-GCM-SHA256"],
            }

            self.enviar_sin_cifrar(json.dumps(mensaje_client_hello))
            print("ClientHello con clave DH enviado")

            # 2. Recibir ServerHello
            data, addr = self.recibir_de()
            if not data or addr != self.addr_servidor:
                print("Error: No se recibió ServerHello")
                return False

            mensaje_servidor = json.loads(data["payload"].decode("utf-8"))
            if mensaje_servidor.get("type") != "server_hello":
                print("Error: ServerHello inválido")
                return False

            # 3. Procesar ServerHello
            self.server_random = base64.b64decode(
                mensaje_servidor["server_random"])
            server_dh_public_key = base64.b64decode(
                mensaje_servidor["dh_public_key"])
            cipher_suite = mensaje_servidor["cipher_suite"]

            print(f"ServerHello recibido con cipher suite: {cipher_suite}")

            # 4. Calcular secreto compartido y derivar claves
            self.tls.set_server_dh_public_key(server_dh_public_key)
            self.tls.derive_master_secret(
                self.client_random, self.server_random)
            self.tls.derive_traffic_keys()

            # 5. Recibir confirmación encriptada del servidor
            data, addr = self.recibir_de()
            if not data:
                print("Error: No se recibió confirmación del servidor")
                return False

            # Descifrar confirmación
            try:
                confirmacion_texto = self.tls.decrypt_data(data["payload"], 0)
                confirmacion = json.loads(confirmacion_texto)

                if (
                    confirmacion.get("type") == "handshake_finished"
                    and confirmacion.get("status") == "success"
                ):
                    print("Handshake TLS 1.3 completado exitosamente")
                    return True
                else:
                    print("Error: Confirmación de handshake inválida")
                    return False
            except Exception as e:
                print(f"Error descifrando confirmación: {e}")
                return False

        except Exception as e:
            print(f"Error en handshake TLS 1.3: {e}")
            return False

    def recibir_archivo(self) -> bool:
        """Recibir archivo con datos AEAD"""
        print("Iniciando recepción de archivo con AEAD...")
        mensaje_counter = 1

        while True:
            try:
                data, addr = self.recibir_de()
                if not data or addr != self.addr_servidor:
                    continue

                seq_recibida = data["header"]["secuencia_propia"]
                print(f"Mensaje AEAD recibido - Seq: {seq_recibida}")

                # Verificar si es mensaje FIN
                if data["header"]["flags"]["FIN"] == 1:
                    print("Señal FIN recibida - Archivo completo")

                    # Enviar ACK para FIN
                    self.informacion_cliente["header"]["flags"]["ACK"] = 1
                    self.informacion_cliente["header"]["secuencia_ACK"] = (
                        seq_recibida + 1
                    )
                    self.informacion_cliente["header"]["secuencia_propia"] += 1

                    header_en_bytes = self.header_a_bytes()
                    self.sock.sendto(header_en_bytes, self.addr_servidor)
                    self.informacion_cliente["header"]["flags"] = {
                        key: 0 for key in self.informacion_cliente["header"]["flags"]
                    }

                    print("ACK para FIN enviado")
                    break

                # Descifrar datos AEAD
                if data["payload"]:
                    try:
                        linea_texto = self.tls.decrypt_data(
                            data["payload"], mensaje_counter - 1
                        )
                        print(f"Recibido (AEAD descifrado): {linea_texto}")
                    except Exception as e:
                        print(f"Error descifrando datos AEAD: {e}")

                # Enviar ACK cifrado
                self.informacion_cliente["header"]["secuencia_ACK"] = seq_recibida + 1
                self.informacion_cliente["header"]["flags"]["ACK"] = 1

                ack_msg = f"ACK:{seq_recibida}"
                self.enviar_cifrado(ack_msg)
                mensaje_counter += 1

            except Exception as e:
                print(f"Error recibiendo datos AEAD: {e}")
                break

        return True

    def cerrar(self):
        self.sock.close()


def main():
    print("=== Cliente TCP con TLS 1.3 + AEAD iniciado ===")

    cliente = TCPCliente(1024)
    cliente.sock.settimeout(10.0)

    mi_seq = random.randint(20000, 30000)
    addr_server = ("127.0.0.1", 20000)

    print(f"Conectando al servidor en {addr_server[0]}:{addr_server[1]}")

    try:
        # 1. Handshake TCP
        if cliente.handshake_cliente(mi_seq, addr_server):
            print("Handshake TCP exitoso")

            # 2. Handshake TLS 1.3
            if cliente.tls_handshake_cliente():
                print("Handshake TLS 1.3 exitoso - Iniciando recepción de archivo AEAD")
                cliente.recibir_archivo()
            else:
                print("Error: No se pudo completar el handshake TLS 1.3")
        else:
            print("Error: No se pudo completar el handshake TCP")

    except Exception as e:
        print(f"Error en cliente: {e}")
    finally:
        cliente.cerrar()
        print("Cliente desconectado")


if __name__ == "__main__":
    main()
