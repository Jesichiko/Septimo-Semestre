from abc import ABC, abstractmethod


class ExecuteOperation(ABC):
    @abstractmethod
    def exec_operation(operations) -> float: ...
