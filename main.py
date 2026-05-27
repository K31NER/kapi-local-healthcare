import os
from server import lifespan
from fastapi import FastAPI
from Config.settings import settings
from fastapi.staticfiles import StaticFiles
from API.routers import user as user_router
from API.routers import chat as chat_router
from API.routers.web import auth as web_auth
from API.routers.web import chat as web_chat
from fastapi.responses import RedirectResponse
from API.routers import report as report_router
from API.routers.web import report as web_report
from API.routers.web._auth import NotAuthenticated
from API.routers.web import profile as web_profile
from API.routers.web import settings as web_settings
from API.routers import knowledge as knowledge_router
from API.routers.web import knowledge as web_knowledge
from API.routers.web import sessions as web_sessions
from starlette.middleware.sessions import SessionMiddleware

SECRET_KEY = settings.SECRET_KEY

app = FastAPI(
    title="Kapi-API",
    description="API para la gestion local de asistentes medico para zonas rurales",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.exception_handler(NotAuthenticated)
async def not_authenticated_handler(request, exc):
    return RedirectResponse(url="/auth/login", status_code=303)

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(user_router.router)
app.include_router(report_router.router)
app.include_router(chat_router.router)
app.include_router(knowledge_router.router)
app.include_router(web_auth.router)
app.include_router(web_chat.router)
app.include_router(web_profile.router)
app.include_router(web_report.router)
app.include_router(web_knowledge.router)
app.include_router(web_settings.router)
app.include_router(web_sessions.router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/chat", status_code=303)

@app.get("/health", status_code=200)
def health():
    return {"msg": "Server is running"}