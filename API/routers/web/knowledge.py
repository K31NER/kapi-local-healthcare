from API.depends import get_add_document
from fastapi.responses import HTMLResponse
from API.routers.web._templates import templates
from API.routers.web._auth import require_session
from Use_cases.knowledge.add_document import AddDocument
from fastapi import APIRouter, Depends, Form, Request, UploadFile

router = APIRouter(tags=["web-knowledge"])


@router.get("/knowledge", include_in_schema=False)
async def knowledge_page(request: Request, _=Depends(require_session)):
    return templates.TemplateResponse(request, "knowledge/index.html", {
        "active_page": "/knowledge",
    })


@router.post("/knowledge/ingest", include_in_schema=False)
async def knowledge_ingest(
    file: UploadFile,
    tipo: str = Form(default="oficial"),
    categoria: str = Form(default="informe_medico"),
    subtipo: str = Form(default="guia"),
    uc: AddDocument = Depends(get_add_document),
    _=Depends(require_session),
):
    content = await file.read()
    metadata = {"tipo": tipo, "categoria": categoria, "subtipo": subtipo}
    try:
        saved_path = uc.execute(content, file.filename, metadata)
        return HTMLResponse(
            f'<div class="px-4 py-2 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700">'
            f'Documento indexado: <code class="font-mono text-xs">{saved_path}</code></div>'
        )
    except ValueError as e:
        return HTMLResponse(
            f'<div class="px-4 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{e}</div>',
            status_code=400,
        )
    except Exception as e:
        return HTMLResponse(
            f'<div class="px-4 py-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">Error al indexar: {e}</div>',
            status_code=500,
        )
