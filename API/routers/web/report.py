from fastapi import APIRouter, Depends, Request
from API.routers.web._templates import templates
from API.routers.web._auth import require_session

router = APIRouter(tags=["web-report"])


@router.get("/report", include_in_schema=False)
async def report_page(request: Request, _=Depends(require_session)):
    return templates.TemplateResponse(request, "report/index.html", {
        "active_page": "/report",
    })
