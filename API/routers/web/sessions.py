from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from API.depends import get_consultation_repo
from API.routers.web._templates import templates
from API.routers.web._auth import require_session
from Repositories.consultation_repository import ConsultationRepository

router = APIRouter(tags=["web-sessions"])


@router.get("/sessions", include_in_schema=False)
async def sessions_page(
    request: Request,
    repo: ConsultationRepository = Depends(get_consultation_repo),
    _=Depends(require_session),
):
    sessions = repo.get_sessions()
    return templates.TemplateResponse(request, "sessions/index.html", {
        "active_page": "/sessions",
        "sessions": sessions,
    })


@router.get("/sessions/{session_id}", include_in_schema=False)
async def session_detail(
    request: Request,
    session_id: str,
    repo: ConsultationRepository = Depends(get_consultation_repo),
    _=Depends(require_session),
):
    consultations = repo.get_by_session(session_id)
    preview = consultations[0].question[:60] if consultations else session_id
    return templates.TemplateResponse(request, "sessions/_history.html", {
        "active_page": "/sessions",
        "session_id": session_id,
        "preview": preview,
        "consultations": consultations,
    })


@router.post("/sessions/{session_id}/resume", include_in_schema=False)
async def session_resume(
    request: Request,
    session_id: str,
    _=Depends(require_session),
):
    request.session["chat_session_id"] = session_id
    return RedirectResponse(url="/chat", status_code=303)


@router.delete("/sessions/{session_id}", include_in_schema=False)
async def session_delete(
    session_id: str,
    repo: ConsultationRepository = Depends(get_consultation_repo),
    _=Depends(require_session),
):
    repo.delete_session(session_id)
    return Response(status_code=200, headers={"HX-Redirect": "/sessions"})


@router.delete("/sessions", include_in_schema=False)
async def sessions_delete_all(
    repo: ConsultationRepository = Depends(get_consultation_repo),
    _=Depends(require_session),
):
    repo.delete_all()
    return Response(status_code=200, headers={"HX-Redirect": "/sessions"})
