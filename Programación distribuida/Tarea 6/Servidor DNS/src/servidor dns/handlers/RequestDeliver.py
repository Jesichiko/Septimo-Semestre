from ..data.Message import Message
from ..network.TCP import Connection


class RequestDeliver:
    def __init__(self, connection: Connection):
        self.connection = connection

    def send_response(self, response: Message):
        ip_port = response["ip"].split(":")
        ip = ip_port[0]
        port = ip_port[1]

        self.connection.sendTo(response.json, (ip, port))

    def receive_response(self, buffer: int) -> dict:
        response = self.connection.ReceiveFrom(buffer)
        return dict(response.decode("utf-8"))
