from datetime import datetime
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

    def get_sessions(self) -> list[dict]:
        rows = self.session.exec(
            select(ConsultationTable)
            .where(ConsultationTable.session_id != "")
            .order_by(ConsultationTable.id.asc())
        ).all()

        sessions: dict[str, dict] = {}
        for row in rows:
            sid = row.session_id
            q = row.question.strip()
            if sid not in sessions:
                sessions[sid] = {
                    "session_id": sid,
                    "preview": (q[:55] + "…") if len(q) > 55 else q,
                    "started_at": row.created_at,
                    "last_at": row.created_at,
                    "count": 1,
                }
            else:
                sessions[sid]["last_at"] = row.created_at
                sessions[sid]["count"] += 1

        # Formato legible para la fecha de última actividad
        for s in sessions.values():
            try:
                dt = datetime.fromisoformat(s["last_at"])
                s["date_label"] = dt.strftime("%d %b  %H:%M")
            except Exception:
                s["date_label"] = s["last_at"][:16]

        return sorted(sessions.values(), key=lambda x: x["last_at"], reverse=True)

    def get_by_session(self, session_id: str) -> list[Consultation]:
        rows = self.session.exec(
            select(ConsultationTable)
            .where(ConsultationTable.session_id == session_id)
            .order_by(ConsultationTable.id.asc())
        ).all()
        return [orm_to_consultation(r) for r in rows]

    def delete_session(self, session_id: str) -> None:
        rows = self.session.exec(
            select(ConsultationTable)
            .where(ConsultationTable.session_id == session_id)
        ).all()
        for row in rows:
            self.session.delete(row)
        self.session.commit()

    def delete_all(self) -> None:
        rows = self.session.exec(select(ConsultationTable)).all()
        for row in rows:
            self.session.delete(row)
        self.session.commit()
