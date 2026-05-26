from fastapi import Depends
from sqlmodel import Session
from Use_cases.user.get_user import GetUser
from Use_cases.chat.stream_chat import StreamChat
from Use_cases.report.export_pdf import ExportPDF
from Use_cases.user.create_user import CreateUser
from Use_cases.user.delete_user import DeleteUser
from Use_cases.user.update_user import UpdateUser
from Repositories.user_repository import UserRepository
from Use_cases.knowledge.add_document import AddDocument
from Infrastructure.Databases.sql.conexion import get_session
from Repositories.knowledge_repository import KnowledgeRepository
from Use_cases.consultation.save_consultation import SaveConsultation
from Repositories.consultation_repository import ConsultationRepository
from Infrastructure.Databases.sql.user_repository import SQLUserRepository
from Infrastructure.Knowledge.chroma_repository import ChromaKnowledgeRepository
from Infrastructure.Databases.sql.consultation_repository import SQLConsultationRepository


def get_user_repo(session: Session = Depends(get_session)) -> UserRepository:
    return SQLUserRepository(session)


def get_consultation_repo(session: Session = Depends(get_session)) -> ConsultationRepository:
    return SQLConsultationRepository(session)


def get_knowledge_repo() -> KnowledgeRepository:
    return ChromaKnowledgeRepository()


def get_create_user(repo: UserRepository = Depends(get_user_repo)) -> CreateUser:
    return CreateUser(repo)


def get_get_user(repo: UserRepository = Depends(get_user_repo)) -> GetUser:
    return GetUser(repo)


def get_update_user(repo: UserRepository = Depends(get_user_repo)) -> UpdateUser:
    return UpdateUser(repo)


def get_delete_user(repo: UserRepository = Depends(get_user_repo)) -> DeleteUser:
    return DeleteUser(repo)


def get_save_consultation(repo: ConsultationRepository = Depends(get_consultation_repo)) -> SaveConsultation:
    return SaveConsultation(repo)


def get_export_pdf(
    user_repo: UserRepository = Depends(get_user_repo),
    consult_repo: ConsultationRepository = Depends(get_consultation_repo),
) -> ExportPDF:
    return ExportPDF(user_repo, consult_repo)


def get_stream_chat(
    consult_repo: ConsultationRepository = Depends(get_consultation_repo),
    user_repo: UserRepository = Depends(get_user_repo),
) -> StreamChat:
    return StreamChat(consult_repo, user_repo)


def get_add_document(
    knowledge_repo: KnowledgeRepository = Depends(get_knowledge_repo),
) -> AddDocument:
    return AddDocument(knowledge_repo)
