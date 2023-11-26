# util/event_manager.py

from typing import Callable, Dict, List, Any
from collections import defaultdict

class EventManager:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = defaultdict(list)

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners[event].append(callback)

    def emit(self, event: str, *args, **kwargs) -> None:
        for listener in self._listeners[event]:
            listener(*args, **kwargs)
