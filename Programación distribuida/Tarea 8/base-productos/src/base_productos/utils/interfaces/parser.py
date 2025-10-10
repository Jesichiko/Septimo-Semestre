from abc import ABC, abstractmethod


class Parser(ABC):
    @abstractmethod
    def create(self, product_id: int, nombre: str, precio: float) -> int: ...

    @abstractmethod
    def insert(self, nombre: str, precio: float) -> int: ...

    @abstractmethod
    def read(self, nombre: str) -> int: ...
