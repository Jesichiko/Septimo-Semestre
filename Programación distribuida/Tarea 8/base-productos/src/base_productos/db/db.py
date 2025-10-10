import os
from ..utils.implementations.xml_parsing import XMLParser


class Database:
    def __init__(self, name: str = "products.xml", dir: str = "db", file_parser=None):
        self.path = os.path.join(dir, name)
        self.file_parser = file_parser or XMLParser(self.path)

    def create_item(self, name: str, precio: int) -> int:
        return self.file_parser.create(nombre=name, precio=precio)

    def insert_item(self, id_product: int, name: str, precio: int) -> int:
        return self.file_parser.insert(
            product_id=id_product, nombre=name, precio=precio
        )

    def search_item(self, name: str) -> int:
        return self.file_parser.read(nombre=name)
