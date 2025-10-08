import os.path
from implementations import XML_Parser as xml


class Database:
    def _check_path(self):
        if not os.path.exists(self.path):
            print("El archivo de base de datos no se encontro, creando uno nuevo...")
            os.mkdir(self.path)

    def __init__(self, name: str = "products.xml", dir: str = "db", parser_file=xml()):
        self.path = "/".join(name, dir)

    def search_item(self, name: str) -> int:
        self._check_path()

    def insert_imte(self, name: str) -> int:
        self._check_path()
