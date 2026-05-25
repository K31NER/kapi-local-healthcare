import json
from Domain.user import User
from datetime import date, datetime
from Domain.consultation import Consultation
from Infrastructure.Databases.sql.models import UserTable, ConsultationTable


def user_to_orm(user: User) -> UserTable:
    return UserTable(
        id=user.id,
        full_name=user.full_name,
        birth_date=user.birth_date.isoformat(),
        gender=user.gender,
        blood_type=user.blood_type,
        allergies=json.dumps(user.allergies),
        chronic_conditions=json.dumps(user.chronic_conditions),
        emergency_contact_name=user.emergency_contact_name,
        emergency_contact_phone=user.emergency_contact_phone,
    )


def orm_to_user(row: UserTable) -> User:
    return User(
        id=row.id,
        full_name=row.full_name,
        birth_date=date.fromisoformat(row.birth_date),
        gender=row.gender,
        blood_type=row.blood_type,
        allergies=json.loads(row.allergies),
        chronic_conditions=json.loads(row.chronic_conditions),
        emergency_contact_name=row.emergency_contact_name,
        emergency_contact_phone=row.emergency_contact_phone,
    )


def consultation_to_orm(c: Consultation) -> ConsultationTable:
    return ConsultationTable(
        id=c.id,
        question=c.question,
        answer=c.answer,
        steps=json.dumps(c.steps),
        summary=json.dumps(c.summary),
        created_at=c.created_at.isoformat(),
    )


def orm_to_consultation(row: ConsultationTable) -> Consultation:
    return Consultation(
        id=row.id,
        question=row.question,
        answer=row.answer,
        steps=json.loads(row.steps),
        summary=json.loads(row.summary),
        created_at=datetime.fromisoformat(row.created_at),
    )
