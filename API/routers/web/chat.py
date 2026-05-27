import uuid
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from API.routers.web._templates import templates
from API.routers.web._auth import require_session

router = APIRouter(tags=["web-chat"])


@router.get("/chat", include_in_schema=False)
async def chat_page(request: Request, _=Depends(require_session)):
    if "chat_session_id" not in request.session:
        request.session["chat_session_id"] = str(uuid.uuid4())
    return templates.TemplateResponse(request, "chat/index.html", {
        "active_page": "/chat",
        "session_id": request.session["chat_session_id"],
    })


@router.post("/chat/send", include_in_schema=False)
async def chat_send(
    request: Request,
    question: str = Form(...),
    session_id: str = Form(...),
    _=Depends(require_session),
):
    return templates.TemplateResponse(request, "chat/_message.html", {
        "question": question,
        "session_id": session_id,
    })


@router.post("/chat/new-session", include_in_schema=False)
async def chat_new_session(request: Request, _=Depends(require_session)):
    new_id = str(uuid.uuid4())
    request.session["chat_session_id"] = new_id
    short = new_id[:8]
    content = (
        f'<input id="chat-session-id" name="session_id" type="hidden" value="{new_id}" hx-swap-oob="outerHTML:#chat-session-id">'
        f'<span id="session-id-label" class="text-xs text-gray-300 font-mono truncate max-w-[200px]" title="{new_id}" hx-swap-oob="outerHTML:#session-id-label">{short}…</span>'
    )
    return Response(content=content, media_type="text/html")
