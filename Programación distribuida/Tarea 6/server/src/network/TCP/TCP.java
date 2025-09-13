import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.PortUnreachableException;
import java.net.SocketAddress;
import java.net.SocketException;
import java.net.SocketTimeoutException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.HashMap;
import java.util.Random;

class TCP {
  private Long MAX_SEQUENCE = (long)Math.pow(2, 32) - 1;
  private DatagramSocket sock;
  private int bind = 0;

  // 15 bytes minimos
  private HashMap<String, Object> header = new HashMap<>() {
    {
      put("port_raiz", null);                      // 16 bits
      put("port_destino", null);                   // 16 bits
      put("number", (long)0);                      // 32 bits
      put("number_ACK", (long)0);                  // 32 bits
      put("flags", new HashMap<String, Object>() { // 3 bits
        {
          put("SYN", (int)0);
          put("ACK", (int)0);
          put("FIN", (int)0);
        }
      });
      put("checksum", null); // 16 bits
      put("data", null);     // cualquier tamaño
    }
  };

  public TCP(int port, InetAddress ip) throws SocketException {
    header.replace("port_raiz", port);
    header.replace("number", new Random().nextLong() & MAX_SEQUENCE);

    sock = new DatagramSocket(port, ip);
    sock.setSoTimeout(5000);
  }


  private boolean isNextSequence(long number, long number_ack) {
    long expected = (number + 1) % (MAX_SEQUENCE + 1);
    return expected == number_ack;
  }

  private int calculateChecksum(HashMap<String, Object> header) {
    // Creamos copia temporal sin checksum para calcularlo
    HashMap<String, Object> tempHeader = new HashMap<>();
    tempHeader.putAll(header);
    tempHeader.put("checksum", 0);

    // Serializamos sin el checksum y calculamos a partir de el
    byte[] headerBytes = MapToBytes(tempHeader);

    int checksum = 0;
    for (int i = 0; i < headerBytes.length; i++) {
      checksum += (headerBytes[i] & 0xFF);
      // Carry wraparound para checksum de 16 bits
      checksum = (checksum & 0xFFFF) + (checksum >> 16);
    }

    // Complemento a 1 de 16 bits
    return (~checksum) & 0xFFFF;
  }

  private boolean validateChecksum(HashMap<String, Object> receivedHeader) {
    int receivedChecksum = (Integer)receivedHeader.get("checksum");
    int calculatedChecksum = calculateChecksum(receivedHeader);
    return receivedChecksum == calculatedChecksum;
  }

  @SuppressWarnings("unchecked")
  private byte[] MapToBytes(HashMap<String, Object> header) {
    // Calculamos tamaño total del mensaje (si es que hay)
    byte[] data = (byte[])header.get("data");
    int dataLength = (data != null) ? data.length : 0;
    int totalSize = 15 + dataLength; // 15 bytes de header fijo + data

    ByteBuffer buffer = ByteBuffer.allocate(totalSize);
    buffer.order(ByteOrder.BIG_ENDIAN); // Network byte order

    // 16 bits: port_raiz
    Integer portRaiz = (Integer)header.get("port_raiz");
    buffer.putShort(portRaiz != null ? portRaiz.shortValue() : (short)0);

    // 16 bits: port_destino
    Integer portDestino = (Integer)header.get("port_destino");
    buffer.putShort(portDestino != null ? portDestino.shortValue() : (short)0);

    // 32 bits: number (TCP sequence)
    Long number = (Long)header.get("number");
    buffer.putInt(number != null ? number.intValue() : 0);

    // 32 bits: number_ACK
    Long numberAck = (Long)header.get("number_ACK");
    buffer.putInt(numberAck != null ? numberAck.intValue() : 0);

    // 3 bits empaquetados en 1 byte: flags
    HashMap<String, Object> flags =
        (HashMap<String, Object>)header.get("flags");
    byte flagByte = 0;
    if (flags != null) {
      if ((Integer)flags.get("SYN") == 1)
        flagByte |= 0x01; // bit 0
      if ((Integer)flags.get("ACK") == 1)
        flagByte |= 0x02; // bit 1
      if ((Integer)flags.get("FIN") == 1)
        flagByte |= 0x04; // bit 2
    }
    buffer.put(flagByte);

    // 16 bits: checksum
    Integer checksum = (Integer)header.get("checksum");
    buffer.putShort(checksum != null ? checksum.shortValue() : (short)0);

    // Data variable
    if (data != null && dataLength > 0) {
      buffer.put(data);
    }

    return buffer.array();
  }

  private HashMap<String, Object> bitsToMap(byte[] bytes)
      throws IllegalArgumentException {

    if (bytes.length < 15) {
      throw new IllegalArgumentException(
          "Error: El mensaje es muy pequeño para ser un mensaje TCP");
    }

    ByteBuffer buffer = ByteBuffer.wrap(bytes);
    buffer.order(ByteOrder.BIG_ENDIAN); // Network byte order

    HashMap<String, Object> header = new HashMap<>();

    // 16 bits: port_raiz
    header.put("port_raiz", (int)(buffer.getShort() & 0xFFFF));

    // 16 bits: port_destino
    header.put("port_destino", (int)(buffer.getShort() & 0xFFFF));

    // 32 bits: number
    header.put("number", (long)(buffer.getInt() & 0xFFFFFFFFL));

    // 32 bits: number_ACK
    header.put("number_ACK", (long)(buffer.getInt() & 0xFFFFFFFFL));

    // 1 byte: flags desempaquetados
    byte flagByte = buffer.get();
    HashMap<String, Object> flags = new HashMap<>();
    flags.put("SYN", (flagByte & 0x01) != 0 ? 1 : 0);
    flags.put("ACK", (flagByte & 0x02) != 0 ? 1 : 0);
    flags.put("FIN", (flagByte & 0x04) != 0 ? 1 : 0);
    header.put("flags", flags);

    // 16 bits: checksum
    header.put("checksum", (int)(buffer.getShort() & 0xFFFF));

    // Data restante (si es que existe)
    int remainingBytes = buffer.remaining();
    if (remainingBytes > 0) {
      byte[] data = new byte[remainingBytes];
      buffer.get(data);
      header.put("data", data);
    } else {
      header.put("data", null);
    }

    return header;
  }

  private DatagramPacket receiveHandshakeMsg(int buffer)
      throws SocketTimeoutException, Exception {
    DatagramPacket payload = new DatagramPacket(new byte[buffer], buffer);
    sock.receive(payload);

    if (payload.getLength() < 15)
      throw new Exception("Error: Tamaño de mensaje TCP invalido");

    return payload;
  }

  public boolean bind() { 

    return sock.isBound(); 
  }

  @SuppressWarnings("unchecked")
  public boolean connect() throws Exception {
    // 1. Aceptamos el SYN del cliente
    DatagramPacket synPeticion = receiveHandshakeMsg(1024);

    // 1.2 Deserializamos el DatagramPacket a HashMap
    HashMap<String, Object> peticion = bitsToMap(synPeticion.getData());

    // 1.2.1 Validamos checksum del SYN
    if (!validateChecksum(peticion)) {
      throw new Exception("SYN corrupto: checksum invalido");
    }

    HashMap<String, Object> synFlags =
        (HashMap<String, Object>)peticion.get("flags");

    // 1.3 Verificamos que la bandera SYN este prendida
    if (!synFlags.get("SYN").equals(1)) {
      return false; // No es un mensaje SYN
    }

    // 1.4 Extraemos el number del cliente
    long numero_client = (long)peticion.get("number");

    // 1.5 Extraemos el puerto del cliente
    header.replace("port_destino", peticion.get("port_raiz"));

    // 2. Enviamos el ACK a su mensaje (SYN-ACK)
    // 2.1 Actualizamos el number ACK de la response a enviar
    header.replace("number_ACK", numero_client + 1);

    // 2.2 Activamos las banderas SYN-ACK
    HashMap<String, Object> synAckFlags =
        (HashMap<String, Object>)header.get("flags");
    synAckFlags.replace("SYN", 1);
    synAckFlags.replace("ACK", 1);

    // 2.3 Calculamos checksum del mensaje a enviar (mensaje vacio, solo header)
    header.replace("checksum", calculateChecksum(header));

    // 2.4 Serializamos el mensaje para poder enviarlo
    byte[] synAckData = MapToBytes(header);

    // 2.5 Enviamos mensaje
    sock.send(new DatagramPacket(synAckData, synAckData.length,
                                 synPeticion.getSocketAddress()));

    // 3. Recibimos ACK final de client
    DatagramPacket ackResponse = receiveHandshakeMsg(1024);

    // 3.1 Deserializamos el mensaje
    HashMap<String, Object> finalAck = bitsToMap(ackResponse.getData());

    // 3.1.1 Validamos checksum del ACK final
    if (!validateChecksum(finalAck)) {
      throw new Exception("ACK final corrupto: checksum inválido");
    }

    // 3.2 Verificamos que su bandera ACK este prendida
    HashMap<String, Object> ackFlags =
        (HashMap<String, Object>)finalAck.get("flags");

    if (!ackFlags.get("ACK").equals(1)) {
      return false; // No es mensaje ACK
    }

    // Verificamos que su number_ACK sea nuestro number + 1
    if (!isNextSequence((long)header.get("number"),
                        (long)finalAck.get("number_ACK"))) {
      return false;
    }

    // CONEXION EXITOSA
    // 3.3 Adoptamos su number_ACK como nuestro number
    header.replace("number", (long)finalAck.get("number_ACK"));

    // 3.4 Adoptamos su number como nuestro number_ACK + 1
    header.replace("number_ACK", (long)finalAck.get("number") + 1);

    // 3.5 Reiniciamos banderas
    HashMap<String, Object> flags =
        (HashMap<String, Object>)header.get("flags");
    flags.replaceAll((_, _) -> 0);

    return true;
  }

  public boolean sendMsg(byte[] payload, SocketAddress addr)
      throws PortUnreachableException, Exception {
    sock.send(new DatagramPacket(payload, payload.length, addr));
    return true;
  }

  public HashMap<String, Object> receiveMsg(int buffer)
      throws SocketTimeoutException, Exception {
    DatagramPacket payload = new DatagramPacket(new byte[buffer], buffer);
    sock.receive(payload);

    // Deserializamos payload
    HashMap<String, Object> message = bitsToMap(payload.getData());

    // Validamos checksum
    if (!validateChecksum(message))
      throw new Exception("Error: Checksum invalido, mensaje invalido");

    // Validamos numbers esperados
    long receivedAck = (long)message.get("number_ACK");
    long numberHeader = (long)header.get("number");
    if (!isNextSequence(numberHeader, receivedAck)){
      throw new Exception("Error: Numero de secuencia incorrecto\nEsperado: " +
                          numberHeader + ", Recibido: " + receivedAck);
    }

    // Adoptamos su number_ACK como nuestro number
    header.replace("number", receivedAck);

    // Adoptamos su number como nuestro number_ACK +1
    header.replace("number_ACK", (long)message.get("number")+1);
    return message;
  }

  public void close() {
    if (sock != null && !sock.isClosed())
      sock.close();
  }
}
