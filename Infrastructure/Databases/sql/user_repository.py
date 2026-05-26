import json
from sqlmodel import Session, select
from Domain.user import CacheUser, User
from Repositories.user_repository import UserRepository
from Infrastructure.Databases.sql.models import UserTable
from Infrastructure.Databases.sql.mappers import user_to_orm, orm_to_user

class SQLUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._cache = {}
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
        
        # Limpiamos el cache
        self._cache = {}
        return orm_to_user(row)

    def delete(self) -> None:
        row = self.session.exec(select(UserTable)).first()
        if row:
            self.session.delete(row)
            self.session.commit()
            self._cache = {}
    
    def get_user_context(self) -> CacheUser | None:
        if "user" in self._cache:
            return self._cache["user"]

        row = self.session.exec(select(UserTable)).first()
        if not row:
            return None

        from datetime import date
        birth_date = date.fromisoformat(row.birth_date)
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

        user_context = CacheUser(
            full_name=row.full_name,
            age=age,
            gender=row.gender,
            blood_type=row.blood_type,
            allergies=json.loads(row.allergies) if row.allergies else [],
            chronic_conditions=json.loads(row.chronic_conditions) if row.chronic_conditions else []
        )
        self._cache["user"] = user_context
        return user_context
        
        