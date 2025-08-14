#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  char respuesta[] = "Recibi tu saludo houston, tranquilty base te saluda :)";
  struct sockaddr_in addr;
  int servidor, cliente;
  char buffer[1024];

  // IPv4, socket de tipo stream, protocolo TCP
  servidor = socket(AF_INET, SOCK_STREAM, 0);
  addr.sin_family = AF_INET;  // IPv4
  addr.sin_addr.s_addr = INADDR_ANY;
  addr.sin_port = htons(8080);  // Puerto

  int bind_exitoso = bind(servidor, (struct sockaddr *)&addr, sizeof(addr));
  listen(servidor, 5);

  printf("Servidor TCP escuchando en puerto 8080...\n");
  while (1) {
    // Conexion aceptada
    cliente = accept(servidor, NULL, NULL);

    // Conexion recibida
    recv(cliente, buffer, sizeof(buffer), 0);
    printf("Recibido: %s\n", buffer);

    // Conexion respondida
    send(cliente, respuesta, sizeof(respuesta), 0);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
  }
  close(servidor);
  return 0;
}
