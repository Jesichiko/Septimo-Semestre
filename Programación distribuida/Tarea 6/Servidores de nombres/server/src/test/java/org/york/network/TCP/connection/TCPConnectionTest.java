package org.york.network.TCP.connection;

import static org.junit.jupiter.api.Assertions.*;

import java.net.SocketException;
import java.net.UnknownHostException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class TCPConnectionTest {

  private TCPServerConnection server;
  private TCPClientConnection client;
  private Thread serverThread;
  private Thread clientThread;

  @BeforeEach
  void setUp() throws SocketException, UnknownHostException {
    // Usar puerto 0 para asignación automática
    server = new TCPServerConnection(0, "localhost");
    int serverPort = server.socket.getLocalPort();
    client = new TCPClientConnection(0, "localhost", serverPort);
  }

  @AfterEach
  void tearDown() {
    // Cerrar sockets explícitamente
    try {
      if (server != null && server.socket != null &&
          !server.socket.isClosed()) {
        server.socket.close();
      }
      if (client != null && client.socket != null &&
          !client.socket.isClosed()) {
        client.socket.close();
      }
    } catch (Exception e) {
      // Ignorar errores de cierre
    }

    if (serverThread != null) {
      serverThread.interrupt();
      try {
        serverThread.join(1000);
      } catch (InterruptedException e) {
        // Ignorar
      }
    }
    if (clientThread != null) {
      clientThread.interrupt();
      try {
        clientThread.join(1000);
      } catch (InterruptedException e) {
        // Ignorar
      }
    }
  }

  @Test
  void testServerCreation() {
    assertNotNull(server);
    assertNotNull(server.socket);
    assertFalse(server.socket.isClosed());
  }

  @Test
  void testClientCreation() {
    assertNotNull(client);
    assertNotNull(client.socket);
    assertFalse(client.socket.isClosed());
  }

  @Test
  void testThreeWayHandshake() throws InterruptedException {
    boolean[] serverResult = { false };
    boolean[] clientResult = { false };
    Exception[] serverException = { null };
    Exception[] clientException = { null };

    serverThread = new Thread(() -> {
      try {
        serverResult[0] = server.accept();
      } catch (Exception e) {
        serverException[0] = e;
      }
    });

    clientThread = new Thread(() -> {
      try {
        Thread.sleep(100); // Dar tiempo al servidor para estar listo
        clientResult[0] = client.connect();
      } catch (Exception e) {
        clientException[0] = e;
      }
    });

    serverThread.start();
    clientThread.start();

    serverThread.join(5000);
    clientThread.join(5000);

    if (serverException[0] != null) {
      fail("Server exception: " + serverException[0].getMessage());
    }
    if (clientException[0] != null) {
      fail("Client exception: " + clientException[0].getMessage());
    }

    assertTrue(serverResult[0], "Server handshake should succeed");
    assertTrue(clientResult[0], "Client handshake should succeed");
  }

  @Test
  void testDataTransmission() throws InterruptedException {
    byte[] testData = "Hello from client".getBytes();
    boolean[] serverAccepted = { false };
    byte[][] receivedData = { null };
    int serverPort = server.socket.getLocalPort();

    serverThread = new Thread(() -> {
      try {
        serverAccepted[0] = server.accept();
        if (serverAccepted[0]) {
          receivedData[0] = server.receiveFrom(1024).getData();
        }
      } catch (Exception e) {
        fail("Server error: " + e.getMessage());
      }
    });

    clientThread = new Thread(() -> {
      try {
        Thread.sleep(100);
        client.connect();
        Thread.sleep(50);
        client.sendTo(testData, serverPort, "localhost");
      } catch (Exception e) {
        fail("Client error: " + e.getMessage());
      }
    });

    serverThread.start();
    clientThread.start();

    serverThread.join(5000);
    clientThread.join(5000);

    assertTrue(serverAccepted[0], "Server should accept connection");
    assertNotNull(receivedData[0], "Should receive data");
  }

  @Test
  void testConnectionClose() throws InterruptedException {
    boolean[] handshakeComplete = { false, false };
    boolean[] closeComplete = { false, false };
    Exception[] exceptions = { null, null };

    serverThread = new Thread(() -> {
      try {
        handshakeComplete[0] = server.accept();
        Thread.sleep(100); // Esperar a que el cliente inicie el cierre
        closeComplete[0] = server.close();
      } catch (Exception e) {
        exceptions[0] = e;
      }
    });

    clientThread = new Thread(() -> {
      try {
        Thread.sleep(100);
        handshakeComplete[1] = client.connect();
        Thread.sleep(200); // Dar tiempo para que se complete la conexión
        closeComplete[1] = client.close();
      } catch (Exception e) {
        exceptions[1] = e;
      }
    });

    serverThread.start();
    clientThread.start();

    serverThread.join(10000);
    clientThread.join(10000);

    if (exceptions[0] != null) {
      fail("Server exception: " + exceptions[0].getMessage());
    }
    if (exceptions[1] != null) {
      fail("Client exception: " + exceptions[1].getMessage());
    }

    assertTrue(handshakeComplete[0] && handshakeComplete[1],
        "Handshake should complete");
    assertTrue(closeComplete[0] && closeComplete[1],
        "Connection should close properly");
  }
}
