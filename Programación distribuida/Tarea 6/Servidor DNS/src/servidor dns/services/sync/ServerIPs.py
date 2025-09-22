import json

import load.Load as load


class ServerIPs:
    def __init__(self, config_file: str) -> None:
        self.config_file: str = config_file
        self.json_config: dict = self._get_dictionary_from_json_file(self)
        self.servers: set(str) = set()
        self.new_servers: set(str) = set()

    def get_servers(self) -> set[str]:
        return self.servers

    def _get_dictionary_from_json_file(self) -> dict:
        try:
            with open(self.config_file, "r") as file:
                self.json_config = json.load(file)
        except FileExistsError:
            raise ValueError("Error: No existe archivo json de servers")

    def load_config_servers(self) -> set[str]:
        self.servers = load.Load.load_config(self.json_config)

        if not self.servers:  # No puede haber comunicacion sin servers
            raise ValueError("Error: No existe archivo de config")
        return self.servers

    def are_new_changes(self) -> bool:
        self.new_servers = load.Load.load_config(self.json_config)
        return self.servers == self.new_servers

    def sync_changes(self) -> None:
        self.servers = self.new_servers.copy()
