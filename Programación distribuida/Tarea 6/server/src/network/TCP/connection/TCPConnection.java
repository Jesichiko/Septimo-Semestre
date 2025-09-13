package connection;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketAddress;
import java.net.SocketException;
import packet.*;

public abstract class TCPConnection {
  private static final Long MAX_SEQUENCE = (long)Math.pow(2, 32) - 1;
  private long lastSequenceNumber, lastAckNumber;
  protected long expectedSequenceNumber;
  DatagramSocket socket;

  protected TCPConnection(int port, InetAddress ip, int timeout)
      throws SocketException {
    this.socket = new DatagramSocket(port, ip);
    setTimeout(timeout);
  }

  public void setTimeout(int timeoutMs) {
    try {
      socket.setSoTimeout(timeoutMs);
    } catch (SocketException e) {
      throw new RuntimeException("Error configurando timeout", e);
    }
  }

  private void updateMySequenceAfterSend(TCPPacket sentPacket) {
    lastSequenceNumber = (lastSequenceNumber + 1) % (MAX_SEQUENCE + 1);
  }

  private void updateMyTrackingAfterReceive(TCPPacket receivedPacket) {
    expectedSequenceNumber =
        (receivedPacket.getSequenceNumber() + 1) % (MAX_SEQUENCE + 1);
    lastAckNumber = expectedSequenceNumber;
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
    updateMySequenceAfterSend(packetWithChecksum);
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
    if (!TCPPacketValidator.validateChecksum(deserializedPacket)) {
      throw new SocketException("Error de checksum en paquete recibido");
    }

    // Validamos secuencias
    if (!TCPPacketValidator.validateSequenceNumbers(
            expectedSequenceNumber - 1, deserializedPacket.getAckNumber())) {
      throw new SocketException("Error de secuencias de paquete esperadas");
    }

    // Actualizamos secuencias:
    updateMyTrackingAfterReceive(deserializedPacket);
    return deserializedPacket;
  }
  
  // Handshakes que son distintos en cliente y server
  protected abstract boolean connect();
  protected abstract boolean close();
}
