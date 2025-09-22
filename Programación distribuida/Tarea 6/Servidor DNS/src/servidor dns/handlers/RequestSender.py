from ..network.TCP.Connection import Connection


class ResponseSender:

    def __init__(self, connection: Connection, processor: RequestProcessor):
        self.connection = connection

    def send_response():
        pass

    def _send_error_response():
        pass

    def _send_file_content():
        pass

    def _send_to_server(self):
        pass

    def _send_to_client(self):
        pass
