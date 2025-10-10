from ..interfaces.time_provider import TimeProvider
from datetime import datetime


class PyTimeProvider(TimeProvider):
    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
