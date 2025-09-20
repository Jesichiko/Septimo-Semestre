package org.york.network.TCP.connection;

import java.io.IOException;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

import org.york.network.TCP.packet.TCPPacket;

public class TCPClientConnection extends TCPConnection{

  private InetAddress serverAddress;
  private int serverPort;

  TCPClientConnection(int port, String addr) throws SocketException, UnknownHostException{
    super(port, InetAddress.getByName(addr));
  }

  public TCPClientConnection(int localPort, String serverAddr, int serverPort) throws SocketException, UnknownHostException {
    super(localPort, InetAddress.getByName("0.0.0.0"));
    this.serverAddress = InetAddress.getByName(serverAddr);
    this.serverPort = serverPort;
  }

  @Override
  protected boolean connect() throws IOException {
    // 3-way handshake por parte del cliente
    
    // 1. Enviar SYN
    TCPPacket synPacket = createControlPacket(serverPort, true, false, false);
    sendPacket(synPacket, new InetSocketAddress(serverAddress, serverPort));

    // 2. Recibir SYN-ACK
    TCPPacket synAckResponse = receivePacket(1024);
    if (!synAckResponse.isSyn() || !synAckResponse.isAck()) {
      throw new IOException("Error 3-way Handshake: Se esperaba SYN-ACK");
    }

    // 3. Enviar ACK final
    TCPPacket finalAck = createControlPacket(serverPort, false, true, false);
    sendPacket(finalAck, new InetSocketAddress(serverAddress, serverPort));

    return true;
  }

  @Override
  public boolean close() throws IOException {
    // 4-way handshake por parte del cliente
    
    // 1. Enviar FIN
    TCPPacket finPacket = createControlPacket(serverPort, false, false, true);
    sendPacket(finPacket, new InetSocketAddress(serverAddress, serverPort));

    // 2. Recibir ACK
    TCPPacket ackResponse = receivePacket(1024);
    if (!ackResponse.isAck()) {
      throw new IOException("Error 4-way Handshake: Se esperaba ACK");
    }

    // 3. Recibir FIN
    TCPPacket finResponse = receivePacket(1024);
    if (!finResponse.isFin()) {
      throw new IOException("Esperaba FIN del servidor");
    }

    // 4. Enviar ACK final
    TCPPacket finalAck = createControlPacket(serverPort, false, true, false);
    sendPacket(finalAck, new InetSocketAddress(serverAddress, serverPort));

    return true;
  }
}
