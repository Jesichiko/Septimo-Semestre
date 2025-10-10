from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def create(self, nombre: str, precio: int) -> int: ...

    @abstractmethod
    def insert(self, product_id: int, nombre: str, precio: int) -> int: ...

    @abstractmethod
    def read(self, nombre: str) -> int: ...
