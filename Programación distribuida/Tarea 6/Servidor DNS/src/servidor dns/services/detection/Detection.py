import os


class Detection:
    def __search_files_in_dir(self, dir: str) -> set(str):
        try:
            if not os.path.isdir(dir):
                return ()

            return (
                file
                for file in os.listdir(dir)
                if os.path.isfile(os.path.join(dir, file))
            )

        except PermissionError:
            return ()

    def __search_servers_in_dict(self, config_file: dict) -> set(str):
        try:
            return set(config_file.get("servers").keys())
        except KeyError:
            raise KeyError("Error: Se eliminaron todos los servers de config")

    def detect(self, target: str | dict) -> set(str) | None:
        if not os.path.exists(target):
            return None

        if isinstance(target, str):
            return self.__search_files_in_dir(target)

        return self.__search_servers_in_dict(target)
