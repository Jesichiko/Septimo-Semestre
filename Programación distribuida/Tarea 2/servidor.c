#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  char respuesta[] =
      "Recibi tu mensaje cliente, saludos desde tranquility base! :)";
  struct sockaddr_in addr;
  int servidor, cliente;
  char buffer[1024];

  servidor = socket(AF_INET, SOCK_STREAM, 0);
  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = INADDR_ANY;  // Aceptar la conexion de cualquier dir
  addr.sin_port = htons(20000);  // Puerto

  int bind_exitoso = bind(servidor, (struct sockaddr *)&addr, sizeof(addr));
  if (bind_exitoso == -1) {
    printf("Error al crear el socket padre del servidor, terminando programa.");
    exit(1);
  }

  listen(servidor, 5);
  printf("Servidor esperando en el puerto 20000...\n");
  while (1) {
    // Conexion aceptada
    cliente = accept(servidor, NULL, NULL);

    // Conexion recibida
    recv(cliente, buffer, sizeof(buffer), 0);
    printf("Recibido del cliente: %s \n", buffer);

    // Conexion respondida
    send(cliente, respuesta, sizeof(respuesta), 0);
    send(cliente, buffer, strlen(buffer), 0);
    close(cliente);
  }
  close(servidor);
  return 0;
}
