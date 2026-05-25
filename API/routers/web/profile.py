from typing import List
from datetime import date
from Domain.user import User
from fastapi.responses import Response
from Use_cases.user.get_user import GetUser
from API.routers.web._templates import templates
from Use_cases.user.update_user import UpdateUser
from Use_cases.user.delete_user import DeleteUser
from API.routers.web._auth import require_session
from Use_cases.user.create_user import CreateUser
from fastapi import APIRouter, Depends, Form, Request
from API.depends import get_create_user, get_get_user, get_update_user, get_delete_user
from API.routers.web._constants import COMMON_ALLERGIES, COMMON_CONDITIONS, BLOOD_TYPES, GENDERS

router = APIRouter(tags=["web-profile"])

_STATIC_CTX = {
    "active_page": "/profile",
    "allergies_options": COMMON_ALLERGIES,
    "conditions_options": COMMON_CONDITIONS,
    "blood_types": BLOOD_TYPES,
    "genders": GENDERS,
}


def _ctx(request: Request, **extra) -> tuple:
    ctx = {"today": date.today().isoformat(), **_STATIC_CTX, **extra}
    return request, ctx


@router.get("/profile", include_in_schema=False)
async def profile_page(
    request: Request,
    get_uc: GetUser = Depends(get_get_user),
    _=Depends(require_session),
):
    user = get_uc.execute()
    req, ctx = _ctx(request, user=user)
    return templates.TemplateResponse(req, "profile/index.html", ctx)


@router.post("/profile", include_in_schema=False)
async def save_profile(
    request: Request,
    full_name: str = Form(...),
    birth_date: str = Form(...),
    gender: str = Form(...),
    blood_type: str = Form(...),
    emergency_contact_name: str = Form(...),
    emergency_contact_phone: str = Form(...),
    allergies: List[str] = Form(default=[]),
    chronic_conditions: List[str] = Form(default=[]),
    get_uc: GetUser = Depends(get_get_user),
    create_uc: CreateUser = Depends(get_create_user),
    update_uc: UpdateUser = Depends(get_update_user),
    _=Depends(require_session),
):
    existing = get_uc.execute()
    user_data = User(
        full_name=full_name.strip(),
        birth_date=date.fromisoformat(birth_date),
        gender=gender,
        blood_type=blood_type,
        allergies=allergies,
        chronic_conditions=chronic_conditions,
        emergency_contact_name=emergency_contact_name.strip(),
        emergency_contact_phone=emergency_contact_phone.strip(),
    )
    try:
        if existing:
            for field in [
                "full_name", "birth_date", "gender", "blood_type",
                "allergies", "chronic_conditions",
                "emergency_contact_name", "emergency_contact_phone",
            ]:
                setattr(existing, field, getattr(user_data, field))
            saved = update_uc.execute(existing)
        else:
            saved = create_uc.execute(user_data)
    except ValueError as e:
        req, ctx = _ctx(request, user=existing, error=str(e))
        return templates.TemplateResponse(req, "profile/_form.html", ctx)

    req, ctx = _ctx(request, user=saved)
    return templates.TemplateResponse(req, "profile/_metrics.html", ctx)


@router.delete("/profile", include_in_schema=False)
async def delete_profile(
    uc: DeleteUser = Depends(get_delete_user),
    _=Depends(require_session),
):
    uc.execute()
    return Response(status_code=200, headers={"HX-Redirect": "/profile"})
