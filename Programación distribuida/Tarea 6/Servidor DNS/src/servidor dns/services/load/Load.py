import os


class Load:
    def __load_servers_from_dict(self, dict_config: dict) -> set[str]:
        try:
            return set(dict_config.get("servers").keys())
        except KeyError:
            raise KeyError("Error: No se encontraron servers en config")

    def __load_config_from_file(self, file: str) -> tuple[set(str), int]:
        with open(file, "r") as warmfile:
            lines = [line.strip().split() for line in warmfile if line.strip()]

            filenames = [parts[0] for parts in lines]
            constant_value = int(lines[0][1]) if lines else 0

            return (filenames, constant_value)

    def load_config(self, target: str | dict) -> tuple[set(str), int] | set(str) | None:

        if not os.path.exists(target):
            return None

        if isinstance(target, str):
            return self.__load_config_from_file(target)

        return self.__load_servers_from_dict(target)
