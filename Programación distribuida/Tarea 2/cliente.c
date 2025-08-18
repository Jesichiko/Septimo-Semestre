#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
  #include <winsock2.h>
  #include <ws2tcpip.h>
  #pragma comment(lib, "ws2_32.lib")
  #define close closesocket
#else
  #include <netinet/in.h>
  #include <sys/socket.h>
  #include <arpa/inet.h>
  #include <unistd.h>
#endif

int main() {
  int sock, conexion_exitosa, mensaje_enviado, mensaje_recibido;
  char mensaje[] = "Hola servidor TCP!";
  struct sockaddr_in addr;
  char respuesta[1024];

#ifdef _WIN32
  WSADATA wsa;
  if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) {
    printf("Error al iniciar Winsock\n");
    return 1;
  }
#endif

  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1) {
    printf("Error al crear el socket, terminando cliente...");
    exit(-1);
  }

  addr.sin_family = AF_INET;
  addr.sin_addr.s_addr = inet_addr("172.26.160.103");
  addr.sin_port = htons(20000);

  // Conectamos al servidor.c
  conexion_exitosa = connect(sock, (struct sockaddr *)&addr, sizeof(addr));
  if (conexion_exitosa == -1) {
    printf("No se puede conectar con el servidor, terminando cliente...");
#ifdef _WIN32
    WSACleanup();
#endif
    exit(-1);
  }

  // Enviamos el mensaje "Hola servidor TCP!"
  mensaje_enviado = send(sock, mensaje, strlen(mensaje), 0);
  if (mensaje_enviado == -1) {
    printf("Error al enviar el mensaje al servidor, terminando cliente...");
#ifdef _WIN32
    WSACleanup();
#endif
    exit(-1);
  }

  // Recibimos una respuesta por parte del servidor
  mensaje_recibido = recv(sock, respuesta, sizeof(respuesta)-1, 0);
  if (mensaje_recibido == -1) {
    printf("Error al recibir el mensaje del servidor");
#ifdef _WIN32
    WSACleanup();
#endif
    exit(-1);
  }
  respuesta[mensaje_recibido] = '\0';
  printf("Respuesta: %s\n", respuesta);

  close(sock);

#ifdef _WIN32
  WSACleanup();
#endif

  return 0;
}
