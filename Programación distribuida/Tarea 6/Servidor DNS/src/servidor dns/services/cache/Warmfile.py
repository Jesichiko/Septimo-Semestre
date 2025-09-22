import load.Load as load


class Warmfile:
    def __init__(self, name_warmfile: str):
        self.name_warmfile = name_warmfile

    def load_warmfile(self) -> tuple[set(str), int] | ():
        config = load.Load.load_config()

        if not config:  # El warmfile puede no existir, despues se crea
            return set()

        return config

    def save_warmfile(self, archivos: set(str), ttl: int) -> None:
        with open(self.name_warmfile, "w") as warmfile:
            for archivo in archivos:
                warmfile.write(f"{archivo} {ttl}\n")
