package org.york.network.TCP.packet;

public class TCPPacketValidator {
  private static final Long MAX_SEQUENCE = (long)Math.pow(2, 32) - 1;

  public static int calculateChecksum(TCPPacket packet) {
    // Serializamos el TCPPacket
    byte[] data = TCPPacketSerializer.serialize(packet.withChecksum(0));

    // Hacemos una checksum sumando cada bit
    int checksum = 0;
    for (byte b : data) {
      checksum += (b & 0xFF);
      checksum = (checksum & 0xFFFF) + (checksum >> 16);
    }

    // Retornamos su complemento a 16 bits
    return (~checksum) & 0xFFFF;
  }

  public static boolean validateChecksum(TCPPacket packet) {
    // Calculamos el checksum del packet y verificamos
    int calculateChecksumd = calculateChecksum(packet.withChecksum(0));
    return calculateChecksumd == packet.getChecksum();
  }

  public static boolean validateSequenceNumbers(long number, long ackNumber) {
    // Hacemos wraparound al number
    long expected = (number + 1) % (MAX_SEQUENCE + 1);
    return expected == ackNumber;
  }
}
