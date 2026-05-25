from typing import Union
from dataclasses import dataclass

@dataclass
class ContentEvent:
    text: str
    session_id: str

@dataclass
class DoneEvent:
    answer: str
    steps: list[str]
    summary: dict
    session_id: str

@dataclass
class ErrorEvent:
    error: str

@dataclass
class ThinkingEvent:
    text: str

ChatEvent = Union[ContentEvent, DoneEvent, ErrorEvent, ThinkingEvent]