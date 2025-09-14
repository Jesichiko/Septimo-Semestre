package org.york.network.TCP.connection;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.SocketAddress;
import java.net.SocketException;
import java.util.Random;

import org.york.network.TCP.packet.*;

public abstract class TCPConnection {
  private static final Long MAX_SEQUENCE = (long)Math.pow(2, 32) - 1;
  private long lastSequenceNumber;
  protected long expectedSequenceNumber;

  private long myNumber, myAckNumber;
  DatagramSocket socket;

  TCPConnection(int port, InetAddress ip) throws SocketException {
    this.socket = new DatagramSocket(port, ip);

    this.myNumber = new Random().nextLong() & MAX_SEQUENCE;
    this.myAckNumber = 0;
  }

  private void updateAfterSend(TCPPacket sentPacket) {
    lastSequenceNumber = (lastSequenceNumber + 1) % (MAX_SEQUENCE + 1);
  }

  private void updateAfterReceive(TCPPacket receivedPacket) {
    expectedSequenceNumber =
        (receivedPacket.getSequenceNumber() + 1) % (MAX_SEQUENCE + 1);
  }

  protected boolean sendPacket(TCPPacket packet, SocketAddress destination)
      throws IOException {
    // Calculamos checksum del paquete y creamos un nuevo paquete:
    int realChecksum = TCPPacketValidator.calculateChecksum(packet);
    TCPPacket packetWithChecksum = packet.withChecksum(realChecksum);

    // Enviamos el paquete:
    byte[] packetToSend = TCPPacketSerializer.serialize(packetWithChecksum);
    socket.send(
        new DatagramPacket(packetToSend, packetToSend.length, destination));

    // Actualizamos secuencias:
    updateAfterSend(packetWithChecksum);
    return true;
  }

  protected TCPPacket receivePacket(int buffer)
      throws IOException, SocketException {
    // Creamos el tamaño del dgram del packet a recibir (buff):
    DatagramPacket dgramBuff = new DatagramPacket(new byte[buffer], buffer);
    socket.receive(dgramBuff);

    // Deserializamos el packet:
    TCPPacket deserializedPacket =
        TCPPacketSerializer.deserialize(dgramBuff.getData());

    // Validamos checksums:
    if (!TCPPacketValidator.validateChecksum(deserializedPacket))
      throw new SocketException("Error de checksum en paquete recibido");

    // Validamos secuencias
    if (!TCPPacketValidator.validateSequenceNumbers(
            expectedSequenceNumber - 1, deserializedPacket.getAckNumber()))
      throw new SocketException("Error de secuencias de paquete esperadas");

    // Actualizamos secuencias:
    updateAfterReceive(deserializedPacket);
    return deserializedPacket;
  }
  
  public boolean sendTo(byte[] data, int port, String addr) throws IOException{
    // Creamos el TCPPacket con la data
    TCPPacket packet = new TCPPacket.Builder()
      .sourcePort(socket.getPort())
      .destinationPort(port)
      .sequenceNumber(myNumber)
      .ackNumber(myAckNumber)
      .syn(false)
      .ack(true)
      .fin(false)
      .data(data)
      .build();

    return sendPacket(packet,new InetSocketAddress(addr, port));
  }
  
  public DatagramPacket receiveFrom(int buffer) throws SocketException, IOException{
    return new DatagramPacket(TCPPacketSerializer.serialize(receivePacket(buffer)), buffer);
  }
  // Handshakes que son distintos en cliente y server
  protected abstract boolean connect();

  public abstract boolean close();
}
