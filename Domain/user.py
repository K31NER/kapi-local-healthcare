from datetime import date
from dataclasses import dataclass

@dataclass
class User:
    full_name: str
    birth_date: date
    gender: str
    blood_type: str
    allergies: list[str]
    chronic_conditions: list[str]
    emergency_contact_name: str
    emergency_contact_phone: str
    id: int | None = None

@dataclass
class CacheUser:
    full_name: str
    age: int
    gender: str
    blood_type: str
    allergies: list[str]
    chronic_conditions: list[str]