package org.york.network.TCP.connection;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.*;
import java.net.SocketException;
import java.net.UnknownHostException;

public class TCPConnectionTest {
    
    private TCPServerConnection server;
    private TCPClientConnection client;
    private Thread serverThread;
    private Thread clientThread;
    
    @BeforeEach
    void setUp() throws SocketException, UnknownHostException {
        server = new TCPServerConnection(8080, "localhost");
        client = new TCPClientConnection(0, "localhost", 8080);
    }
    
    @AfterEach
    void tearDown() {
        if (serverThread != null) serverThread.interrupt();
        if (clientThread != null) clientThread.interrupt();
    }
    
    @Test
    void testServerCreation() {
        assertNotNull(server);
    }
    
    @Test
    void testClientCreation() {
        assertNotNull(client);
    }
    
    @Test
    void testThreeWayHandshake() throws InterruptedException {
        boolean[] serverResult = {false};
        boolean[] clientResult = {false};
        Exception[] serverException = {null};
        Exception[] clientException = {null};
        
        serverThread = new Thread(() -> {
            try {
                serverResult[0] = server.accept();
            } catch (Exception e) {
                serverException[0] = e;
            }
        });
        
        clientThread = new Thread(() -> {
            try {
                Thread.sleep(100);
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
        boolean[] serverAccepted = {false};
        byte[][] receivedData = {null};
        
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
                client.sendTo(testData, 8080, "localhost");
            } catch (Exception e) {
                fail("Client error: " + e.getMessage());
            }
        });
        
        serverThread.start();
        clientThread.start();
        
        serverThread.join(5000);
        clientThread.join(5000);
        
        assertTrue(serverAccepted[0]);
        assertNotNull(receivedData[0]);
    }
    
    @Test
    void testConnectionClose() throws InterruptedException {
        boolean[] handshakeComplete = {false, false};
        boolean[] closeComplete = {false, false};
        
        serverThread = new Thread(() -> {
            try {
                handshakeComplete[0] = server.accept();
                closeComplete[0] = server.close();
            } catch (Exception e) {
                fail("Server error: " + e.getMessage());
            }
        });
        
        clientThread = new Thread(() -> {
            try {
                Thread.sleep(100);
                handshakeComplete[1] = client.connect();
                Thread.sleep(100);
                closeComplete[1] = client.close();
            } catch (Exception e) {
                fail("Client error: " + e.getMessage());
            }
        });
        
        serverThread.start();
        clientThread.start();
        
        serverThread.join(10000);
        clientThread.join(10000);
        
        assertTrue(handshakeComplete[0] && handshakeComplete[1]);
        assertTrue(closeComplete[0] && closeComplete[1]);
    }
}
