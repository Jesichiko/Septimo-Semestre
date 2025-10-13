import os
import threading
import xml.etree.ElementTree as ET
from ..interfaces import Parser


class XMLParser(Parser):
    # Parser XML thread-safe para operaciones concurrentes.
    def __init__(self, filepath: str):
        # Inicializamos el parser XML
        self.filepath = filepath
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            print("Archivo XML de la base de datos no existe, creando uno nuevo...")
            os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

            with self._lock:
                root = ET.Element("productos")
                tree = ET.ElementTree(root)
                ET.indent(tree, space="    ")
                tree.write(self.filepath, encoding="UTF-8", xml_declaration=True)

    def _parse(self) -> ET.ElementTree:
        # Lee y parsea el archivo XML, retornando un arbol del archivo xml
        try:
            return ET.parse(self.filepath)
        except ET.ParseError as e:
            print(f"[ERROR] XML mal formado: {e}")
            print("[INFO] Regenerando archivo XML...")
            root = ET.Element("productos")
            tree = ET.ElementTree(root)
            self._save(tree)
            return tree

    def _save(self, tree: ET.ElementTree):
        ET.indent(tree, space="    ")
        tree.write(self.filepath, encoding="UTF-8", xml_declaration=True)

    def create(self, nombre: str, precio: int) -> int:
        with self._lock:
            tree = self._parse()
            root = tree.getroot()

            # Obtenemos todos los IDs existentes
            ids = []
            for p in root.findall("producto"):
                try:
                    ids.append(int(p.get("id")))
                except (ValueError, TypeError):
                    pass

            # Generamos nuevo ID
            new_id = max(ids, default=0) + 1

            # Creamos nuevo producto
            producto = ET.SubElement(root, "producto", id=str(new_id))
            ET.SubElement(producto, "nombre").text = nombre
            ET.SubElement(producto, "precio").text = str(precio)

            # Guardamos cambios
            self._save(tree)
            print(
                f"++ [CREACION] Se creo producto\n\t -> Id:{new_id}, "
                f"Producto:{nombre}, Precio:{precio}\n"
            )
            return new_id

    def insert(self, product_id: int, nombre: str, precio: int) -> int:
        with self._lock:
            tree = self._parse()
            root = tree.getroot()

            # Verificamos que el ID no exista
            existing = root.find(f"./producto[@id='{product_id}']")
            if existing is not None:
                error_msg = f"El producto con ID {product_id} ya existe"
                print(f"[ERROR] {error_msg}")
                raise ValueError(error_msg)

            # Creamos nuevo producto con ID específico
            producto = ET.SubElement(root, "producto", id=str(product_id))
            ET.SubElement(producto, "nombre").text = nombre
            ET.SubElement(producto, "precio").text = str(precio)

            # Guardamos cambios
            self._save(tree)
            print(
                f"++ [INSERCION] Se inserto producto\n\t -> Id:{product_id}, "
                f"Producto:{nombre}, Precio:{precio}\n"
            )
            return product_id

    def read(self, nombre: str) -> int:
        with self._lock:
            tree = self._parse()
            root = tree.getroot()

            # Buscamos producto por nombre
            for producto in root.findall("producto"):
                nombre_elem = producto.find("nombre")
                if (
                    nombre_elem is not None
                    and nombre_elem.text
                    and nombre_elem.text.lower() == nombre.lower()
                ):
                    product_id = int(producto.get("id"))
                    print(
                        f"++ [CONSULTA] Producto '{nombre}' encontrado con id:{
                            product_id
                        }"
                    )
                    return product_id

            print(f'-- [CONSULTA] No se encontro el producto "{nombre}"')
            return -1
