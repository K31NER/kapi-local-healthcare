import json
from Domain.user import User
from sqlmodel import Session, select
from Repositories.user_repository import UserRepository
from Infrastructure.Databases.sql.models import UserTable
from Infrastructure.Databases.sql.mappers import user_to_orm, orm_to_user


class SQLUserRepository(UserRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> User:
        existing = self.session.exec(select(UserTable)).first()
        if existing:
            existing.full_name = user.full_name
            existing.birth_date = user.birth_date.isoformat()
            existing.gender = user.gender
            existing.blood_type = user.blood_type
            existing.allergies = json.dumps(user.allergies)
            existing.chronic_conditions = json.dumps(user.chronic_conditions)
            existing.emergency_contact_name = user.emergency_contact_name
            existing.emergency_contact_phone = user.emergency_contact_phone
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return orm_to_user(existing)
        row = user_to_orm(user)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return orm_to_user(row)

    def get(self) -> User | None:
        row = self.session.exec(select(UserTable)).first()
        return orm_to_user(row) if row else None

    def update(self, user: User) -> User:
        row = self.session.exec(select(UserTable)).first()
        if not row:
            raise ValueError("No existe perfil de usuario para actualizar")
        row.full_name = user.full_name
        row.birth_date = user.birth_date.isoformat()
        row.gender = user.gender
        row.blood_type = user.blood_type
        row.allergies = json.dumps(user.allergies)
        row.chronic_conditions = json.dumps(user.chronic_conditions)
        row.emergency_contact_name = user.emergency_contact_name
        row.emergency_contact_phone = user.emergency_contact_phone
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return orm_to_user(row)

    def delete(self) -> None:
        row = self.session.exec(select(UserTable)).first()
        if row:
            self.session.delete(row)
            self.session.commit()
