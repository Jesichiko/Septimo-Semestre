package org.york.network.TCP.packet;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class TCPPacketTest {
    
    private TCPPacket.Builder builder;
    
    @BeforeEach
    void setUp() {
        builder = new TCPPacket.Builder()
            .sourcePort(8080)
            .destinationPort(9090);
    }
    
    @Test
    void testPacketCreation() {
        TCPPacket packet = builder
            .sequenceNumber(100L)
            .ackNumber(200L)
            .syn(true)
            .build();
            
        assertEquals(8080, packet.getSourcePort());
        assertEquals(9090, packet.getDestinationPort());
        assertEquals(100L, packet.getSequenceNumber());
        assertEquals(200L, packet.getAckNumber());
        assertTrue(packet.isSyn());
        assertFalse(packet.isAck());
        assertFalse(packet.isFin());
    }
    
    @Test
    void testPacketWithData() {
        byte[] testData = "Hello TCP".getBytes();
        TCPPacket packet = builder
            .data(testData)
            .build();
            
        assertArrayEquals(testData, packet.getData());
    }
    
    @Test
    void testPacketWithChecksum() {
        TCPPacket originalPacket = builder.build();
        TCPPacket packetWithChecksum = originalPacket.withChecksum(12345);
        
        assertEquals(12345, packetWithChecksum.getChecksum());
        assertEquals(originalPacket.getSourcePort(), packetWithChecksum.getSourcePort());
    }
    
    @Test
    void testBuilderValidation() {
        assertThrows(IllegalStateException.class, () -> {
            new TCPPacket.Builder().build();
        });
    }
    
    @Test
    void testSerializationDeserialization() {
        byte[] testData = "Test message".getBytes();
        TCPPacket originalPacket = builder
            .sequenceNumber(500L)
            .ackNumber(600L)
            .syn(true)
            .ack(false)
            .fin(false)
            .checksum(1234)
            .data(testData)
            .build();
            
        byte[] serialized = TCPPacketSerializer.serialize(originalPacket);
        TCPPacket deserializedPacket = TCPPacketSerializer.deserialize(serialized);
        
        assertEquals(originalPacket.getSourcePort(), deserializedPacket.getSourcePort());
        assertEquals(originalPacket.getDestinationPort(), deserializedPacket.getDestinationPort());
        assertEquals(originalPacket.getSequenceNumber(), deserializedPacket.getSequenceNumber());
        assertEquals(originalPacket.getAckNumber(), deserializedPacket.getAckNumber());
        assertEquals(originalPacket.isSyn(), deserializedPacket.isSyn());
        assertEquals(originalPacket.isAck(), deserializedPacket.isAck());
        assertEquals(originalPacket.isFin(), deserializedPacket.isFin());
        assertEquals(originalPacket.getChecksum(), deserializedPacket.getChecksum());
        assertArrayEquals(originalPacket.getData(), deserializedPacket.getData());
    }
}
