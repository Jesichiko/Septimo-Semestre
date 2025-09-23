import json
import socket
import sys
import time
from typing import Optional


class DNSClient:
    def __init__(self, server_ip: str = "192.168.1.100", server_port: int = 50000):
        self.server_ip = server_ip
        self.server_port = server_port
        self.timeout = 10  # segundos

    def send_request(self, request: dict) -> Optional[dict]:
        """Envía una petición al servidor DNS y retorna la respuesta"""
        try:
            # Crear socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            # Convertir request a JSON y enviar
            request_json = json.dumps(request, indent=2)
            print(f"📤 Enviando petición a {self.server_ip}:{self.server_port}")
            print(f"📝 Request:\n{request_json}\n")

            sock.sendto(
                request_json.encode("utf-8"), (self.server_ip, self.server_port)
            )

            # Recibir respuesta
            response_data, server_address = sock.recvfrom(4096)
            response = json.loads(response_data.decode("utf-8"))

            sock.close()
            return response

        except socket.timeout:
            print(
                f"❌ Timeout: El servidor no respondió en {
                    self.timeout} segundos"
            )
            return None

        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON: {e}")
            return None

        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return None

    def print_response(self, response: dict):
        """Formatea e imprime la respuesta del servidor"""
        if not response:
            return

        print("📥 Respuesta recibida:")
        print(f"📝 Response:\n{json.dumps(response, indent=2)}")

        # Análisis de la respuesta
        status = response.get("status", "UNKNOWN")
        authority = response.get("authority", "unknown")
        files = response.get("files", [])
        server_ip = response.get("ip", "unknown")

        print("\n📊 Análisis de la respuesta:")
        print(f"   Status: {status}")
        print(f"   Autoridad: {authority}")
        print(f"   Servidor: {server_ip}")
        print(f"   Archivos encontrados: {len(files)}")

        if files:
            print("   Lista de archivos:")
            for i, file in enumerate(files, 1):
                print(f"      {i}. {file}")
        else:
            print("   ⚠️  No se encontraron archivos")
        print()

    def test_find_file(self, filename: str):
        """Prueba buscar un archivo específico"""
        print(f"🔍 TEST: Buscar archivo '{filename}'")
        print("=" * 50)

        request = {
            "type_request": "peticion",
            "target": "client",
            "status": "",
            "authority": "",
            "files": [filename],
            "ip": "client",
        }

        response = self.send_request(request)
        self.print_response(response)
        return response

    def test_find_multiple_files(self, filenames: list):
        """Prueba buscar múltiples archivos"""
        print(f"🔍 TEST: Buscar múltiples archivos {filenames}")
        print("=" * 50)

        request = {
            "type_request": "peticion",
            "target": "client",
            "status": "",
            "authority": "",
            "files": filenames,
            "ip": "client",
        }

        response = self.send_request(request)
        self.print_response(response)
        return response

    def test_list_all_files(self):
        """Prueba listar todos los archivos del sistema"""
        print("🔍 TEST: Listar todos los archivos del sistema distribuido")
        print("=" * 50)

        request = {
            "type_request": "peticion",
            "target": "client",
            "status": "",
            "authority": "",
            "files": "all",
            "ip": "client",
        }

        response = self.send_request(request)
        self.print_response(response)
        return response

    def test_nonexistent_file(self):
        """Prueba buscar un archivo que no existe"""
        print("🔍 TEST: Buscar archivo inexistente")
        print("=" * 50)

        request = {
            "type_request": "peticion",
            "target": "client",
            "status": "",
            "authority": "",
            "files": ["archivo_que_no_existe.txt"],
            "ip": "client",
        }

        response = self.send_request(request)
        self.print_response(response)
        return response

    def run_all_tests(self):
        """Ejecuta todos los tests disponibles"""
        print("🚀 INICIANDO TESTS DEL CLIENTE DNS")
        print("=" * 60)

        tests = [
            ("Buscar archivo existente", lambda: self.test_find_file("Ejemplo.txt")),
            (
                "Buscar múltiples archivos",
                lambda: self.test_find_multiple_files(["Hola.txt", "Ipsum.txt"]),
            ),
            ("Listar todos los archivos", self.test_list_all_files),
            ("Buscar archivo inexistente", self.test_nonexistent_file),
        ]

        results = []
        for test_name, test_func in tests:
            print(f"\n🧪 Ejecutando: {test_name}")
            try:
                response = test_func()
                success = response is not None and response.get("status") != "ERROR"
                results.append((test_name, success, response))
                print("Test completado\n")
            except Exception as e:
                print(f"Test falló: {e}\n")
                results.append((test_name, False, None))

            time.sleep(1)  # Pausa entre tests

        # Resumen de resultados
        print("=" * 60)
        print("📋 RESUMEN DE TESTS:")
        print("=" * 60)

        passed = 0
        for test_name, success, response in results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status}: {test_name}")
            if success:
                passed += 1

        print(f"\nResultados: {passed}/{len(results)} tests pasaron")

        if passed == len(results):
            print(
                "¡Todos los tests pasaron! El servidor está funcionando correctamente."
            )
        else:
            print(" Algunos tests fallaron. Revisa la configuración del servidor.")


def show_help():
    """Muestra la ayuda del cliente"""
    help_text = """
🔧 Cliente DNS de Prueba - Ayuda
================================

Uso: python cliente.py [comando] [argumentos]

Comandos disponibles:
  find <archivo>              - Buscar un archivo específico
  find-multi <arch1,arch2>    - Buscar múltiples archivos (separados por comas)
  list-all                    - Listar todos los archivos del sistema
  test-missing                - Probar con archivo inexistente
  run-tests                   - Ejecutar todos los tests automáticamente
  help                        - Mostrar esta ayuda

Ejemplos:
  python cliente.py find Ejemplo.txt
  python cliente.py find-multi Hola.txt,Ipsum.txt
  python cliente.py list-all
  python cliente.py run-tests

Configuración:
  - Por defecto se conecta a 192.168.1.100:50000
  - Puedes cambiar la IP/puerto editando el código
"""
    print(help_text)


def main():
    # Configuración del cliente
    SERVER_IP = "192.168.1.100"  # Cambia por la IP de tu servidor
    SERVER_PORT = 50000

    client = DNSClient(SERVER_IP, SERVER_PORT)

    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    try:
        if command == "find" and len(sys.argv) >= 3:
            filename = sys.argv[2]
            client.test_find_file(filename)

        elif command == "find-multi" and len(sys.argv) >= 3:
            filenames = sys.argv[2].split(",")
            filenames = [f.strip() for f in filenames]  # Limpiar espacios
            client.test_find_multiple_files(filenames)

        elif command == "list-all":
            client.test_list_all_files()

        elif command == "test-missing":
            client.test_nonexistent_file()

        elif command == "run-tests":
            client.run_all_tests()

        elif command == "help":
            show_help()

        else:
            print("❌ Comando no reconocido")
            show_help()

    except KeyboardInterrupt:
        print("\n👋 Cliente terminado por el usuario")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
