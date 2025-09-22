import socket


class Connection:
    def __init__(self, UDP_PORT, UDP_IP):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))

    def sendTo(self, data, destino):
        self.sock.sendto(data, destino)

    def ReceiveFrom(self, buffer: int) -> bytes:
        return self.sock.recv(buffer)
