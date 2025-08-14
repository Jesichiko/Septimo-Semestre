#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  int sock;
  struct sockaddr_in addr;
  char mensaje[] = "Hola servidor TCP!";
  char respuesta[1024];

  sock = socket(AF_INET, SOCK_STREAM, 0);

  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  addr.sin_port = htons(8080);

  // Conectamos al servidor.c
  int conexion_exitosa = connect(sock, (struct sockaddr *)&addr, sizeof(addr));

  // Enviamos el mensaje "Hola servidor TCP!"
  send(sock, mensaje, strlen(mensaje), 0);

  // Recibimos una respuesta por parte del cliente
  recv(sock, respuesta, sizeof(respuesta), 0);
  printf("Respuesta: %s\n", respuesta);

  close(sock);
  return 0;
}
