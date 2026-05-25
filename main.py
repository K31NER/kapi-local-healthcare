from server import lifespan
from fastapi import FastAPI, Depends
from API.routers import user as user_router
from API.routers import chat as chat_router
from Domain.consultation import Consultation
from API.depends import get_save_consultation
from API.routers import report as report_router
from API.routers import knowledge as knowledge_router
from Use_cases.consultation.save_consultation import SaveConsultation


app = FastAPI(
    title="Kapi-API",
    description="API para la gestion local de asistentes medico para zonas rurales",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(user_router.router)
app.include_router(report_router.router)
app.include_router(chat_router.router)
app.include_router(knowledge_router.router)


@app.get("/health", status_code=200)
def health():
    return {"msg": "Server is running"}