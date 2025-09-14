package org.york.network.TCP.connection;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

import org.york.network.TCP.packet.TCPPacket;

public class TCPServerConnection extends TCPConnection {

  private int port;
  TCPServerConnection(int port, String addr) throws SocketException, UnknownHostException {
    super(port, InetAddress.getByName(addr));
    this.port = port;
  }

  public boolean accept() throws SocketException, IOException {
    return connect();
  }

  @Override
  protected boolean connect() throws SocketException, IOException {
    // Aceptamos el SYN del cliente
    TCPPacket synRequest = receivePacket(1024);

    if(!synRequest.isSyn())
      throw new Exception("Error al recibir el 3-way handshake, primer mensaje no es syn");

    // Enviamos un SYN-ACK
    TCPPacket synResponse = new TCPPacket.Builder()
      .sourcePort(port)
      .destinationPort(synRequest.getSourcePort())
      .build();
      

    return true;
  }

  @Override
  public boolean close() {
    // 4-way handshake por parte del servidor

    return true;
  }
}
