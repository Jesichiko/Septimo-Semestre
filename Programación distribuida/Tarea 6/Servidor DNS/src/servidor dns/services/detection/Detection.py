import os


class Detection:
    @staticmethod
    def _search_files_in_dir(dir: str) -> set[str]:
        try:
            if not os.path.isdir(dir):
                return set()

            return {
                file
                for file in os.listdir(dir)
                if os.path.isfile(os.path.join(dir, file))
            }

        except PermissionError:
            return set()

    @staticmethod
    def _search_servers_in_dict(config_file: dict) -> set[str]:
        try:
            return set(config_file.get("servers", []))
        except (KeyError, AttributeError):
            raise KeyError("Error: Se eliminaron todos los servers de config")

    @staticmethod
    def detect(target: str | dict) -> set[str] | None:
        if isinstance(target, str):
            if not os.path.exists(target):
                return None
            return Detection._search_files_in_dir(target)

        if isinstance(target, dict):
            return Detection._search_servers_in_dict(target)

        return None
