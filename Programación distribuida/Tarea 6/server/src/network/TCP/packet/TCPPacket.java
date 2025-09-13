package packet;

public class TCPPacket {
  private final Integer sourcePort, destinationPort;
  private final Long sequenceNumber, ackNumber;
  private final boolean syn, ack, fin;
  private final Integer checksum;
  private final byte[] data;

  private TCPPacket(Builder builder) {
    this.sourcePort = builder.sourcePort;
    this.destinationPort = builder.destinationPort;
    this.sequenceNumber = builder.sequenceNumber;
    this.ackNumber = builder.ackNumber;
    this.syn = builder.syn;
    this.ack = builder.ack;
    this.fin = builder.fin;
    this.checksum = builder.checksum;
    this.data = builder.data != null ? builder.data.clone() : null;
  }

  public Integer getSourcePort() { return sourcePort; }

  public Integer getDestinationPort() { return destinationPort; }

  public Long getSequenceNumber() { return sequenceNumber; }

  public Long getAckNumber() { return ackNumber; }

  public boolean isSyn() { return syn; }

  public boolean isAck() { return ack; }

  public boolean isFin() { return fin; }

  public Integer getChecksum() { return checksum; }

  public byte[] getData() { return data != null ? data.clone() : null; }

  public static class Builder {
    private Integer sourcePort;
    private Integer destinationPort;
    private Long sequenceNumber = 0L;
    private Long ackNumber = 0L;
    private boolean syn = false;
    private boolean ack = false;
    private boolean fin = false;
    private Integer checksum = 0;
    private byte[] data;

    public Builder sourcePort(Integer port) {
      this.sourcePort = port;
      return this;
    }

    public Builder destinationPort(Integer port) {
      this.destinationPort = port;
      return this;
    }

    public Builder sequenceNumber(Long seq) {
      this.sequenceNumber = seq;
      return this;
    }

    public Builder ackNumber(Long ack) {
      this.ackNumber = ack;
      return this;
    }

    public Builder syn(boolean syn) {
      this.syn = syn;
      return this;
    }

    public Builder ack(boolean ack) {
      this.ack = ack;
      return this;
    }

    public Builder fin(boolean fin) {
      this.fin = fin;
      return this;
    }

    public Builder checksum(Integer checksum) {
      this.checksum = checksum;
      return this;
    }

    public Builder data(byte[] data) {
      this.data = data;
      return this;
    }

    public TCPPacket build() {
      if (sourcePort == null || destinationPort == null)
        throw new IllegalStateException("Puertos son obligatorios");
      if (sequenceNumber == null || ackNumber == null)
        throw new IllegalStateException("Secuencias obligatoria");

      return new TCPPacket(this);
    }
  }

  public TCPPacket withChecksum(Integer newChecksum) {
    return new Builder()
        .sourcePort(this.sourcePort)
        .destinationPort(this.destinationPort)
        .sequenceNumber(this.sequenceNumber)
        .ackNumber(this.ackNumber)
        .syn(this.syn)
        .ack(this.ack)
        .fin(this.fin)
        .checksum(newChecksum)
        .data(this.data)
        .build();
  }
}
