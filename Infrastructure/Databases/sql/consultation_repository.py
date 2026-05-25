from sqlmodel import Session, select
from Domain.consultation import Consultation
from Infrastructure.Databases.sql.models import ConsultationTable
from Repositories.consultation_repository import ConsultationRepository
from Infrastructure.Databases.sql.mappers import consultation_to_orm, orm_to_consultation

class SQLConsultationRepository(ConsultationRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, consultation: Consultation) -> Consultation:
        row = consultation_to_orm(consultation)
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return orm_to_consultation(row)

    def get_all(self) -> list[Consultation]:
        rows = self.session.exec(select(ConsultationTable)).all()
        return [orm_to_consultation(r) for r in rows]
