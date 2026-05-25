from dataclasses import dataclass
from datetime import datetime


@dataclass
class Consultation:
    question: str
    answer: str
    steps: list[str]
    summary: dict[str, str]
    created_at: datetime
    id: int | None = None
