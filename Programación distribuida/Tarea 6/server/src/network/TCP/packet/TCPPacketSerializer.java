package packet;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class TCPPacketSerializer {
  private static final int HEADER_SIZE = 15; // bits

  public static byte[] serialize(TCPPacket packet) {
    byte[] data = packet.getData();
    int dataLength = (data != null) ? data.length : 0;
    int totalSize = HEADER_SIZE + dataLength;

    ByteBuffer buffer = ByteBuffer.allocate(totalSize);
    buffer.order(ByteOrder.BIG_ENDIAN);

    // Serializamos campos
    buffer.putShort(packet.getSourcePort().shortValue());
    buffer.putShort(packet.getDestinationPort().shortValue());
    buffer.putInt(packet.getSequenceNumber().intValue());
    buffer.putInt(packet.getAckNumber().intValue());

    // Flags empaquetados
    byte flagByte = 0;
    if (packet.isSyn())
      flagByte |= 0x01;
    if (packet.isAck())
      flagByte |= 0x02;
    if (packet.isFin())
      flagByte |= 0x04;
    buffer.put(flagByte);

    // Checksum
    buffer.putShort(packet.getChecksum().shortValue());

    if (data != null)
      buffer.put(data);

    return buffer.array();
  }

  public static TCPPacket deserialize(byte[] bytes)
      throws IllegalArgumentException {
    if (bytes.length < HEADER_SIZE)
      throw new IllegalArgumentException("Mensaje muy pequeño para TCP");

    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    buffer.order(ByteOrder.BIG_ENDIAN);

    // Deserializamos campos de bits:
    int sourcePort = buffer.getShort() & 0xFFFF;
    int destPort = buffer.getShort() & 0xFFFF;
    long seqNum = buffer.getInt() & 0xFFFFFFFFL;
    long ackNum = buffer.getInt() & 0xFFFFFFFFL;

    byte flagByte = buffer.get();
    boolean syn = (flagByte & 0x01) != 0;
    boolean ack = (flagByte & 0x02) != 0;
    boolean fin = (flagByte & 0x04) != 0;

    int checksum = buffer.getShort() & 0xFFFF;

    byte[] data = null;
    if (buffer.hasRemaining()) {
      data = new byte[buffer.remaining()];
      buffer.get(data);
    }

    return new TCPPacket.Builder()
        .sourcePort(sourcePort)
        .destinationPort(destPort)
        .sequenceNumber(seqNum)
        .ackNumber(ackNum)
        .syn(syn)
        .ack(ack)
        .fin(fin)
        .checksum(checksum)
        .data(data)
        .build();
  }
}
