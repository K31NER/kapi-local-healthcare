from fastapi.responses import Response
from API.depends import get_delete_user
from fastapi import APIRouter, Depends, Request
from API.routers.web._templates import templates
from Use_cases.user.delete_user import DeleteUser
from API.routers.web._auth import require_session
from API.routers.web._pin import delete_credentials

router = APIRouter(tags=["web-settings"])

@router.get("/settings", include_in_schema=False)
async def settings_page(request: Request, _=Depends(require_session)):
    return templates.TemplateResponse(request, "settings/index.html", {
        "active_page": "/settings",
    })

@router.delete("/settings/account", include_in_schema=False)
async def delete_account(
    request: Request,
    uc: DeleteUser = Depends(get_delete_user),
    _=Depends(require_session),
):
    try:
        uc.execute()
    except Exception:
        pass
    delete_credentials()
    request.session.clear()
    return Response(status_code=200, headers={"HX-Redirect": "/auth/login"})
