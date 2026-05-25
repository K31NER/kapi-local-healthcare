from typing import Annotated
from Config.settings import settings
from sqlmodel import SQLModel, create_engine, Session

engine = create_engine(settings.DB_URI, echo=True, connect_args={"check_same_thread": False})

def get_session():
    """Crear conexion con la base de datos"""
    with Session(engine) as session:
        yield session

def init_db():
    from Infrastructure.Databases.sql.models import UserTable, ConsultationTable  # noqa: F401
    print("Creando Tablas")
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas con exito")


connection = Annotated[Session, get_session]
