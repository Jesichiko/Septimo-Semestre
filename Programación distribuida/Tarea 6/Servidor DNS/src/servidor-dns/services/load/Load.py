import os


class Load:
    @staticmethod
    def _load_servers_from_dict(dict_config: dict) -> set[str]:
        try:
            return set(dict_config.get("servers"))
        except (KeyError, AttributeError):
            raise KeyError("Error: No se encontraron servers en config")

    @staticmethod
    def _load_config_from_file(file: str) -> tuple[set[str], int]:
        with open(file, "r") as warmfile:
            lines = [line.strip().split() for line in warmfile if line.strip()]

            if not lines:
                return set(), 0

            filenames = {parts[0] for parts in lines}
            constant_value = int(lines[0][1]) if lines else 0

            return filenames, constant_value

    @staticmethod
    def load_config(target: str | dict) -> tuple[set[str], int] | set[str] | None:
        if isinstance(target, str):
            if not os.path.exists(target):
                return None
            return Load._load_config_from_file(target)

        if isinstance(target, dict):
            return Load._load_servers_from_dict(target)

        return None
