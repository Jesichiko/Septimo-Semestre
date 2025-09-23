import os

from load.Load import Load


class Warmfile:
    @staticmethod
    def load_warmfile(name_warmfile: str) -> tuple[set, int] | None:
        if not os.path.exists(name_warmfile):
            return None

        try:
            result = Load.load_config(name_warmfile)
            if result is None:
                return None

            config, ttl_seconds = result
            return config, ttl_seconds

        except Exception:
            return None

    @staticmethod
    def save_warmfile(name_warmfile: str, archivos: set, ttl: int) -> None:
        try:
            with open(name_warmfile, "w") as warmfile:
                for archivo in archivos:
                    warmfile.write(f"{archivo} {ttl}\n")
        except Exception as e:
            print(f"Error guardando warmfile: {e}")
