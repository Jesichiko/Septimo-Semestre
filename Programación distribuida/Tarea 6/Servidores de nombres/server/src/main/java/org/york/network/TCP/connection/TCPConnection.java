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
  private static final Long MAX_SEQUENCE = (long) Math.pow(2, 32) - 1;
  protected long expectedSequenceNumber;

  private long myNumber, myAckNumber;
  DatagramSocket socket;

  TCPConnection(int port, InetAddress ip) throws SocketException {
    this.socket = new DatagramSocket(port, ip);

    this.myNumber = new Random().nextLong() & MAX_SEQUENCE;
    this.expectedSequenceNumber = 0;
    this.myAckNumber = 0;
  }

  private void updateAfterSend(TCPPacket sentPacket) {
    byte[] data = sentPacket.getData();
    int dataLength = (data != null) ? data.length : 0;
    if (sentPacket.isSyn() || sentPacket.isFin()) {
      dataLength = 1;
    }
    this.myNumber = (this.myNumber + dataLength) % (MAX_SEQUENCE + 1);
  }

  protected void updateAfterReceive(TCPPacket receivedPacket) {
    byte[] data = receivedPacket.getData();
    int dataLength = (data != null) ? data.length : 0;
    if (receivedPacket.isSyn() || receivedPacket.isFin()) {
      dataLength = 1;
    }
    expectedSequenceNumber = (receivedPacket.getSequenceNumber() + dataLength) % (MAX_SEQUENCE + 1);
    this.myAckNumber = expectedSequenceNumber;
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
    TCPPacket deserializedPacket = TCPPacketSerializer.deserialize(dgramBuff.getData());

    // Validamos checksums:
    if (!TCPPacketValidator.validateChecksum(deserializedPacket))
      throw new SocketException("Error de checksum en paquete recibido");

    // Validamos secuencias
    if (expectedSequenceNumber != 0 &&
        deserializedPacket.getSequenceNumber() != expectedSequenceNumber) {
      throw new SocketException("Error de secuencias de paquete esperadas");
    }

    // Actualizamos secuencias:
    updateAfterReceive(deserializedPacket);
    return deserializedPacket;
  }

  private TCPPacket createDataPacket(byte[] data, int port) {
    return new TCPPacket.Builder()
        .sourcePort(socket.getLocalPort())
        .destinationPort(port)
        .sequenceNumber(myNumber)
        .ackNumber(myAckNumber)
        .syn(false)
        .ack(true)
        .fin(false)
        .data(data)
        .build();
  }

  protected TCPPacket createControlPacket(int destinationPort, boolean syn,
      boolean ack, boolean fin) {
    return new TCPPacket.Builder()
        .sourcePort(socket.getLocalPort())
        .destinationPort(destinationPort)
        .sequenceNumber(myNumber)
        .ackNumber(myAckNumber)
        .syn(syn)
        .ack(ack)
        .fin(fin)
        .build();
  }

  public boolean sendTo(byte[] data, int port, String addr) throws IOException {
    // Creamos el TCPPacket con la data
    TCPPacket packet = createDataPacket(data, port);
    return sendPacket(packet, new InetSocketAddress(addr, port));
  }

  public DatagramPacket receiveFrom(int buffer)
      throws SocketException, IOException {
    return new DatagramPacket(
        TCPPacketSerializer.serialize(receivePacket(buffer)), buffer);
  }

  // Handshakes que son distintos en cliente y server
  protected abstract boolean connect() throws IOException;

  public abstract boolean close() throws IOException;
}
