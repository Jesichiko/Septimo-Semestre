import load.Load as load


class Warmfile:
    def load_warmfile(self, name_warmfile) -> tuple[set(str), int] | None:
        config, ttl_seconds = load.Load.load_config(name_warmfile)

        if not config:  # El warmfile puede no existir, despues se crea
            return None

        return config, ttl_seconds

    def save_warmfile(self, name_warmfile, archivos: set(str), ttl: int) -> None:
        with open(name_warmfile, "w") as warmfile:
            for archivo in archivos:
                warmfile.write(f"{archivo} {ttl}\n")
