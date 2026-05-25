from API.depends import get_add_document
from Use_cases.knowledge.add_document import AddDocument
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

@router.post("/upload", status_code=201)
async def upload_document(
    file: UploadFile,
    tipo: str = Form(default="oficial"),
    categoria: str = Form(default="informe_medico"),
    subtipo: str = Form(default="guia"),
    uc: AddDocument = Depends(get_add_document),
):
    """Sube un PDF, lo guarda en Infrastructure/Agents/knowledge/docs/ e indexa en agno."""
    content = await file.read()
    metadata = {"tipo": tipo, "categoria": categoria, "subtipo": subtipo}

    try:
        saved_path = uc.execute(content, file.filename, metadata)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al indexar: {e}")

    return {"msg": "Documento indexado correctamente", "path": saved_path}
