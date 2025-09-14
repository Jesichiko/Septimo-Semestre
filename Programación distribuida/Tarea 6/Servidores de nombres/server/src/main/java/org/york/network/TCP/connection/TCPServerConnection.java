package org.york.network.TCP.connection;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.SocketException;
import java.net.UnknownHostException;

import org.york.network.TCP.packet.*;

public class TCPServerConnection extends TCPConnection {

  private InetAddress clientAddress;
  private int clientPort;

  TCPServerConnection(int port, String addr) throws SocketException, UnknownHostException {
    super(port, InetAddress.getByName(addr));
  }

  public boolean accept() throws SocketException, IOException {
    return connect();
  }

  @Override
  protected boolean connect() throws SocketException, IOException {
    // Creamos el buffer para recibir el datagrama
    DatagramPacket dgramBuff = new DatagramPacket(new byte[1024], 1024);
    socket.receive(dgramBuff);
    
    // Obtenemos la dirección del cliente del datagrama
    this.clientAddress = dgramBuff.getAddress();
    
    // Deserializamos el packet SYN
    TCPPacket synRequest = TCPPacketSerializer.deserialize(dgramBuff.getData());

    if(!synRequest.isSyn())
      throw new IOException("Error 3-way Handshake: No se recibio SYN al inicio");

    this.clientPort = synRequest.getSourcePort();

    // Validamos checksums:
    if (!TCPPacketValidator.validateChecksum(synRequest))
      throw new SocketException("Error de checksum en paquete recibido");

    // Actualizamos secuencias después de recibir SYN
    updateAfterReceive(synRequest);

    // Enviamos un SYN-ACK
    TCPPacket synAckResponse = createControlPacket(clientPort, true, true, false);
    sendPacket(synAckResponse, new InetSocketAddress(clientAddress, clientPort));

    // Recibir ACK final
    TCPPacket finalAck = receivePacket(1024);
    if (!finalAck.isAck()) {
      throw new IOException("Error 3-way Handshake: No se recibio ACK");
    }

    return true;
  }

  @Override
  public boolean close() throws IOException {
    // 4-way handshake por parte del servidor
    
    // 1. Recibir FIN del cliente
    TCPPacket finRequest = receivePacket(1024);
    if (!finRequest.isFin()) {
      throw new IOException("Esperaba FIN del cliente");
    }

    // 2. Enviar ACK
    TCPPacket ackResponse = createControlPacket(clientPort, false, true, false);
    sendPacket(ackResponse, new InetSocketAddress(clientAddress, clientPort));

    // 3. Enviar FIN
    TCPPacket finResponse = createControlPacket(clientPort, false, false, true);
    sendPacket(finResponse, new InetSocketAddress(clientAddress, clientPort));

    // 4. Recibir ACK final
    TCPPacket finalAck = receivePacket(1024);
    if (!finalAck.isAck()) {
      throw new IOException("Error 4-way Handshake: No se recibio ACK final del cierre");
    }

    return true;
  }
}
