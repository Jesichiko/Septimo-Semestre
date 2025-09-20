package org.york.network.TCP.packet;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

public class TCPPacketValidatorTest {
    
    private TCPPacket testPacket;
    
    @BeforeEach
    void setUp() {
        testPacket = new TCPPacket.Builder()
            .sourcePort(8080)
            .destinationPort(9090)
            .sequenceNumber(1000L)
            .ackNumber(2000L)
            .syn(true)
            .ack(false)
            .fin(false)
            .data("Test data".getBytes())
            .build();
    }
    
    @Test
    void testCalculateChecksum() {
        int checksum = TCPPacketValidator.calculateChecksum(testPacket);
        
        // El checksum debe ser un número válido de 16 bits
        assertTrue(checksum >= 0 && checksum <= 0xFFFF);
        
        // Calcular dos veces debe dar el mismo resultado
        int checksum2 = TCPPacketValidator.calculateChecksum(testPacket);
        assertEquals(checksum, checksum2);
    }
    
    @Test
    void testValidateChecksumValid() {
        // Calcular checksum correcto
        int correctChecksum = TCPPacketValidator.calculateChecksum(testPacket);
        TCPPacket packetWithChecksum = testPacket.withChecksum(correctChecksum);
        
        // Debe validar como correcto
        assertTrue(TCPPacketValidator.validateChecksum(packetWithChecksum));
    }
    
    @Test
    void testValidateChecksumInvalid() {
        // Usar checksum incorrecto
        TCPPacket packetWithBadChecksum = testPacket.withChecksum(12345);
        
        // Debe validar como incorrecto (a menos que por casualidad sea correcto)
        int correctChecksum = TCPPacketValidator.calculateChecksum(testPacket);
        if (correctChecksum != 12345) {
            assertFalse(TCPPacketValidator.validateChecksum(packetWithBadChecksum));
        }
    }
    
    @Test
    void testValidateSequenceNumbers() {
        // Casos válidos
        assertTrue(TCPPacketValidator.validateSequenceNumbers(99L, 100L));
        assertTrue(TCPPacketValidator.validateSequenceNumbers(0L, 1L));
        
        // Caso de wraparound válido
        long maxSeq = (long) Math.pow(2, 32) - 1;
        assertTrue(TCPPacketValidator.validateSequenceNumbers(maxSeq, 0L));
        
        // Casos inválidos
        assertFalse(TCPPacketValidator.validateSequenceNumbers(100L, 99L));
        assertFalse(TCPPacketValidator.validateSequenceNumbers(100L, 102L));
    }
    
    @Test
    void testChecksumWithDifferentData() {
        TCPPacket packet1 = new TCPPacket.Builder()
            .sourcePort(8080)
            .destinationPort(9090)
            .data("Data 1".getBytes())
            .build();
            
        TCPPacket packet2 = new TCPPacket.Builder()
            .sourcePort(8080)
            .destinationPort(9090)
            .data("Data 2".getBytes())
            .build();
            
        int checksum1 = TCPPacketValidator.calculateChecksum(packet1);
        int checksum2 = TCPPacketValidator.calculateChecksum(packet2);
        
        // Diferentes datos deben producir diferentes checksums
        assertNotEquals(checksum1, checksum2);
    }
    
    @Test
    void testChecksumWithEmptyData() {
        TCPPacket packetWithoutData = new TCPPacket.Builder()
            .sourcePort(8080)
            .destinationPort(9090)
            .build();
            
        int checksum = TCPPacketValidator.calculateChecksum(packetWithoutData);
        TCPPacket packetWithChecksum = packetWithoutData.withChecksum(checksum);
        
        assertTrue(TCPPacketValidator.validateChecksum(packetWithChecksum));
    }
}
