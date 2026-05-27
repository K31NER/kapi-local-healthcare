import json
import uuid
from API.depends import get_stream_chat
from API.schemas.chat import ChatStreamInput
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, BackgroundTasks
from Use_cases.chat.stream_chat import StreamChat, ContentEvent, DoneEvent, ThinkingEvent

router = APIRouter(prefix="/chat", tags=["chat"])


def _event_to_sse(event) -> str:
    if isinstance(event, ThinkingEvent):
        return f"event: thinking\ndata: {json.dumps({'text': event.text})}\n\n"
    if isinstance(event, ContentEvent):
        payload = json.dumps({"text": event.text, "session_id": event.session_id})
        return f"event: content\ndata: {payload}\n\n"
    if isinstance(event, DoneEvent):
        payload = json.dumps({
            "answer": event.answer,
            "steps": event.steps,
            "summary": event.summary,
            "status": event.status,
            "session_id": event.session_id,
        })
        return f"event: done\ndata: {payload}\n\n"
    payload = json.dumps({"error": event.error})
    return f"event: error\ndata: {payload}\n\n"


@router.post("/stream")
def chat_stream(
    data: ChatStreamInput,
    background_tasks: BackgroundTasks,
    stream_uc: StreamChat = Depends(get_stream_chat),
):
    session_id = data.session_id or str(uuid.uuid4())

    # Llamada eager: registra background_tasks antes de retornar StreamingResponse,
    # garantizando que FastAPI capture la tarea de post-procesado.
    event_generator = stream_uc.execute(data.question, session_id, data.user_id, background_tasks)

    def generate():
        for event in event_generator:
            yield _event_to_sse(event)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
