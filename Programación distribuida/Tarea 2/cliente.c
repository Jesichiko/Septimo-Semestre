#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

int main() {
  int sock, conexion_exitosa, mensaje_enviado, mensaje_recibido;
  char mensaje[] = "Hola servidor TCP!";
  struct sockaddr_in addr;
  char respuesta[1024];

  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
    printf("Error al crear el socket, terminando cliente...");
    exit(-1);
  }

  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = inet_addr("127.0.0.1");
  addr.sin_port = htons(20000);

  // Conectamos al servidor.c
  conexion_exitosa = connect(sock, (struct sockaddr *)&addr, sizeof(addr));
  if (conexion_exitosa == -1) {
    printf("No se puede conectar con el servidor, terminando cliente...");
    exit(-1);
  }

  // Enviamos el mensaje "Hola servidor TCP!"
  mensaje_enviado = send(sock, mensaje, strlen(mensaje), 0);
  if (mensaje_enviado == -1) {
    printf("Error al enviar el mensaje al servidor, terminando cliente...");
    exit(-1);
  }

  // Recibimos una respuesta por parte del cliente
  mensaje_recibido = recv(sock, respuesta, sizeof(respuesta), 0);
  if (mensaje_recibido == -1) {
    printf("Error al recibir el mensaje del servidor");
    exit(-1);
  }
  printf("Respuesta: %s\n", respuesta);

  close(sock);
  return 0;
}
