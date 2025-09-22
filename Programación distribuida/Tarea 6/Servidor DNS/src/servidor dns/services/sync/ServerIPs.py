import load.Load as load


class ServerIPs:
    def load_config_servers(self, config: dict) -> None:
        config = load.Load.load_config(config)

        if not config:  # No puede haber comunicacion sin servers
            raise ValueError("Error: No existe archivo de config")

        return config
