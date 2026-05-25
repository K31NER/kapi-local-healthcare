from Domain.consultation import Consultation
from Repositories.consultation_repository import ConsultationRepository

class SaveConsultation:
    def __init__(self, repo: ConsultationRepository):
        self.repo = repo

    def execute(self, consultation: Consultation) -> Consultation:
        return self.repo.save(consultation)
