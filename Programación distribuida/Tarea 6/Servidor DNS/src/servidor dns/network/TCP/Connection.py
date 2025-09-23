import socket


class Connection:
    def __init__(self, UDP_PORT, UDP_IP):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))

    def sendTo(self, data: bytes, destino: tuple) -> None:
        self.sock.sendto(data, destino)

    def ReceiveFrom(self, buffer: int) -> tuple[bytes, tuple]:
        return self.sock.recvfrom(buffer)
