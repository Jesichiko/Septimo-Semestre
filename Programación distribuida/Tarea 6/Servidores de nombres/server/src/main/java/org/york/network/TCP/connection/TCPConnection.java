package org.york.network.TCP.connection;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.SocketException;
import java.util.Random;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;
import org.york.network.TCP.packet.TCPPacket;
import org.york.network.TCP.packet.TCPPacketSerializer;
import org.york.network.TCP.packet.TCPPacketValidator;

public abstract class TCPConnection {
  protected static final long MAX_SEQUENCE = 0xFFFFFFFFL; // 2^32 - 1

  // Sequence state
  protected long sendSeq;
  protected long recvNext = -1L;
  protected long sendAck;

  // connection state
  protected volatile boolean connected = false;
  protected InetSocketAddress peerAddress =
      null; // remote endpoint once connected

  protected DatagramSocket socket;
  protected BlockingQueue<DatagramPacket> receiveQueue = null;

  protected int handshakeTimeoutMs = 2000;

  TCPConnection(int port, InetAddress ip) throws SocketException {
    this(new DatagramSocket(port, ip));
  }

  TCPConnection(DatagramSocket sharedSocket) {
    this.socket = sharedSocket;
    this.sendSeq = new Random().nextLong() & MAX_SEQUENCE;
    this.recvNext = -1L;
    this.sendAck = 0L;
  }

  protected void setReceiveQueue(BlockingQueue<DatagramPacket> queue,
                                 InetSocketAddress peer) {
    this.receiveQueue = queue;
    this.peerAddress = peer;
  }

  private void updateAfterSend(TCPPacket sentPacket) {
    this.sendSeq = (sentPacket.getSequenceNumber() + 1) & MAX_SEQUENCE;
  }

  protected void updateAfterReceive(TCPPacket receivedPacket) {
    this.recvNext = (receivedPacket.getSequenceNumber() + 1) & MAX_SEQUENCE;
    this.sendAck = this.recvNext;
  }

  protected DatagramPacket receiveDatagram(int buffer, int timeoutMs)
      throws IOException {
    if (receiveQueue != null) {
      try {
        DatagramPacket p;

        p = timeoutMs <= 0
                ? receiveQueue.take()
                : receiveQueue.poll(timeoutMs, TimeUnit.MILLISECONDS);
        if (p == null)
          throw new java.net.SocketTimeoutException(
              "Error: Se alcanzo el timeout para recibir datagrama");
        return p;
      } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
        throw new IOException("Error: Se interrumpio la entrega del dgram", e);
      }

    } else {
      if (timeoutMs > 0)
        socket.setSoTimeout(timeoutMs);

      DatagramPacket dgramBuff = new DatagramPacket(new byte[buffer], buffer);
      socket.receive(dgramBuff);

      if (timeoutMs > 0)
        socket.setSoTimeout(0);

      return dgramBuff;
    }
  }

  protected TCPPacket receivePacket(int buffer, int timeoutMs)
      throws IOException {

    // Recibimos un datagrama
    DatagramPacket dgramBuff = receiveDatagram(buffer, timeoutMs);

    // Copiamos el datagrama
    byte[] raw = new byte[dgramBuff.getLength()];
    System.arraycopy(dgramBuff.getData(), 0, raw, 0, dgramBuff.getLength());

    // Deserializamos el packet
    TCPPacket deserializedPacket = TCPPacketSerializer.deserialize(raw);

    // Verificamos checksum del Packet
    if (!TCPPacketValidator.validateChecksum(deserializedPacket))
      throw new SocketException("Error de checksum en paquete recibido");

    // Sacamos la direccion de la peticion del Packet
    InetSocketAddress src =
        new InetSocketAddress(dgramBuff.getAddress(), dgramBuff.getPort());

    // Si ya estamos conectados pero no con la direccion actual entonces
    // ignoramos
    if (connected && !src.equals(peerAddress)) {
      throw new SocketException(
          "Error: Packet ilegal de endpoint no conectado" + src);
    }

    // Si no estamos conectados y el Packet no tiene bandera syn entonces
    // ignoramos
    if (!connected && !deserializedPacket.isSyn()) {
      throw new SocketException(
          "Error: Se recibio packet ilegal antes del handshake");
    }

    // 
    if (recvNext != -1L && !deserializedPacket.isSyn() &&
        !deserializedPacket.isFin()) {
      if (deserializedPacket.getSequenceNumber() != recvNext) {
        throw new SocketException(
            "Error de secuencias de paquete esperadas (esperado=" + recvNext +
            ", recibido=" + deserializedPacket.getSequenceNumber() + ")");
      }
    }

    // Actualizamos secuencias
    updateAfterReceive(deserializedPacket);
    return deserializedPacket;
  }

  protected boolean sendPacket(TCPPacket packet, InetSocketAddress destination)
      throws IOException {
    // Calculamos checksum del paquete y creamos un nuevo paquete:
    int realChecksum = TCPPacketValidator.calculateChecksum(packet);
    TCPPacket packetWithChecksum = packet.withChecksum(realChecksum);

    // Enviamos el paquete:
    byte[] packetToSend = TCPPacketSerializer.serialize(packetWithChecksum);
    DatagramPacket dgram =
        new DatagramPacket(packetToSend, packetToSend.length,
                           destination.getAddress(), destination.getPort());
    socket.send(dgram);

    // Actualizamos secuencias:
    updateAfterSend(packetWithChecksum);
    return true;
  }

  protected TCPPacket createDataPacket(byte[] data, int port) {
    // Creamos Packet con data dada y port dado
    return new TCPPacket.Builder()
        .sourcePort(socket.getLocalPort())
        .destinationPort(port)
        .sequenceNumber(sendSeq)
        .ackNumber(sendAck)
        .syn(false)
        .ack(true)
        .fin(false)
        .data(data)
        .build();
  }

  protected TCPPacket createControlPacket(int destinationPort, boolean syn,
                                          boolean ack, boolean fin) {
    // Creamos Packet de control (sin data, para handshakes)
    return new TCPPacket.Builder()
        .sourcePort(socket.getLocalPort())
        .destinationPort(destinationPort)
        .sequenceNumber(sendSeq)
        .ackNumber(sendAck)
        .syn(syn)
        .ack(ack)
        .fin(fin)
        .build();
  }

  public boolean sendTo(byte[] data, int port, String addr) throws IOException {
    // Envua un paquete de datos a una direccion concreta
    TCPPacket packet = createDataPacket(data, port);
    return sendPacket(packet, new InetSocketAddress(addr, port));
  }

  public boolean send(byte[] data) throws IOException {
    // Verificamos que ya se conecto con un endpoint 
    if (!connected || peerAddress == null)
      throw new IOException("Error: No se ha creado el socket");
    
    // Creamos nuevo packet y lo enviamos
    TCPPacket packet = createDataPacket(data, peerAddress.getPort());
    return sendPacket(packet, peerAddress);
  }

  public DatagramPacket receiveFrom(int buffer)
      throws SocketException, IOException {
    // Creamos un buffer Packet para recibir el mensaje
    TCPPacket p = receivePacket(buffer, 0);
    // Retornamos el datagrama enviado
    return new DatagramPacket(TCPPacketSerializer.serialize(p), buffer);
  }

  // Handshakes que son distintos en cliente y server
  protected abstract boolean connect() throws IOException;

  public abstract boolean close() throws IOException;
}
