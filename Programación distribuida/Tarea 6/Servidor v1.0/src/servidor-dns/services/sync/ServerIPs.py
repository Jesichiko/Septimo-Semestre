import json

from ..load.Load import Load


class ServerIPs:
    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.json_config: dict = {}
        self.servers: set[str] = set()
        self.new_servers: set[str] = set()

    def get_servers(self) -> set[str]:
        return self.servers

    def _get_dictionary_from_json_file(self) -> dict:
        try:
            with open(self.config_file, "r") as file:
                self.json_config = json.load(file)
                return self.json_config
        except FileNotFoundError:
            raise ValueError("Error: No existe archivo json de servers")

    def load_config_servers(self) -> set[str]:
        self.json_config = self._get_dictionary_from_json_file()
        self.servers = Load.load_config(self.json_config)

        if self.servers is None:  # No puede haber comunicacion sin servers
            raise ValueError("Error: No hay servidores configurados")
        return self.servers

    def are_new_changes(self) -> bool:
        self.json_config = self._get_dictionary_from_json_file()
        self.new_servers = Load.load_config(self.json_config)

        if self.new_servers is None:
            raise ValueError("Error: No hay servidores configurados")
        return self.servers != self.new_servers

    def sync_changes(self) -> None:
        if self.new_servers is None:
            raise ValueError("Error: No hay servidores configurados")
        self.servers = self.new_servers.copy()
