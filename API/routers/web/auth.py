import re
from datetime import date
from Domain.user import User
from API.depends import get_create_user
from fastapi.responses import RedirectResponse
from API.routers.web._templates import templates
from Use_cases.user.create_user import CreateUser
from fastapi import APIRouter, Depends, Form, Request
from API.routers.web._pin import is_registered, save_pin, check_pin
from API.routers.web._constants import COMMON_ALLERGIES, COMMON_CONDITIONS

router = APIRouter(tags=["web-auth"])


def _format_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    if len(digits) > 11:
        return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
    return raw


@router.get("/auth/login", include_in_schema=False)
async def login_page(request: Request):
    if request.session.get("authenticated"):
        return RedirectResponse(url="/chat", status_code=303)
    if is_registered():
        return templates.TemplateResponse(request, "auth/login.html",
            {"partial": "auth/_login_form.html", "error": None})
    return templates.TemplateResponse(request, "auth/login.html",
        {"partial": "auth/_register_step1.html",
        "today": date.today().isoformat(), "initial": {}, "error": None})


@router.post("/auth/login", include_in_schema=False)
async def login_submit(request: Request, pin: str = Form(...)):
    if check_pin(pin):
        request.session["authenticated"] = True
        return RedirectResponse(url="/chat", status_code=303)
    return templates.TemplateResponse(request, "auth/login.html",
        {"partial": "auth/_login_form.html", "error": "PIN incorrecto."})


@router.get("/auth/register/step1", include_in_schema=False)
async def register_step1_get(request: Request):
    reg = request.session.get("reg_data", {})
    return templates.TemplateResponse(request, "auth/_register_step1.html",
        {"today": date.today().isoformat(), "initial": reg, "error": None})


@router.post("/auth/register/step1", include_in_schema=False)
async def register_step1_post(
    request: Request,
    full_name: str = Form(...),
    birth_date: str = Form(...),
    gender: str = Form(...),
    blood_type: str = Form(...),
):
    if not full_name.strip():
        return templates.TemplateResponse(request, "auth/_register_step1.html",
            {"today": date.today().isoformat(),
            "initial": {"full_name": full_name, "birth_date": birth_date,
                        "gender": gender, "blood_type": blood_type},
            "error": "El nombre completo es obligatorio."})
    request.session["reg_data"] = {
        "full_name": full_name.strip(),
        "birth_date": birth_date,
        "gender": gender,
        "blood_type": blood_type,
    }
    return templates.TemplateResponse(request, "auth/_register_step2.html",
        {"allergies_options": COMMON_ALLERGIES,
        "conditions_options": COMMON_CONDITIONS, "error": None})


@router.get("/auth/register/step2", include_in_schema=False)
async def register_step2_get(request: Request):
    return templates.TemplateResponse(request, "auth/_register_step2.html",
        {"allergies_options": COMMON_ALLERGIES,
        "conditions_options": COMMON_CONDITIONS, "error": None})


@router.post("/auth/register/step2", include_in_schema=False)
async def register_step2_post(
    request: Request,
    emergency_contact_name: str = Form(...),
    emergency_contact_phone: str = Form(...),
    allergies: list[str] = Form(default=[]),
    chronic_conditions: list[str] = Form(default=[]),
):
    if not emergency_contact_name.strip() or not emergency_contact_phone.strip():
        return templates.TemplateResponse(request, "auth/_register_step2.html",
            {"allergies_options": COMMON_ALLERGIES,
            "conditions_options": COMMON_CONDITIONS,
            "error": "El contacto de emergencia y su teléfono son obligatorios."})
    reg = request.session.get("reg_data", {})
    reg.update({
        "allergies": allergies,
        "chronic_conditions": chronic_conditions,
        "emergency_contact_name": emergency_contact_name.strip(),
        "emergency_contact_phone": _format_phone(emergency_contact_phone),
    })
    request.session["reg_data"] = reg
    return templates.TemplateResponse(request, "auth/_register_step3.html", {"error": None})

@router.get("/auth/register/step3", include_in_schema=False)
async def register_step3_get(request: Request):
    return templates.TemplateResponse(request, "auth/_register_step3.html", {"error": None})


@router.post("/auth/register/step3", include_in_schema=False)
async def register_step3_post(
    request: Request,
    pin1: str = Form(...),
    pin2: str = Form(...),
    create_uc: CreateUser = Depends(get_create_user),
):
    if len(pin1) < 4:
        return templates.TemplateResponse(request, "auth/login.html",
            {"partial": "auth/_register_step3.html",
            "error": "El PIN debe tener al menos 4 caracteres."})
    if pin1 != pin2:
        return templates.TemplateResponse(request, "auth/login.html",
            {"partial": "auth/_register_step3.html", "error": "Los PINs no coinciden."})

    reg = request.session.get("reg_data", {})
    if not reg:
        return RedirectResponse(url="/auth/login", status_code=303)

    try:
        create_uc.execute(User(
            full_name=reg["full_name"],
            birth_date=date.fromisoformat(reg["birth_date"]),
            gender=reg["gender"],
            blood_type=reg["blood_type"],
            allergies=reg.get("allergies", []),
            chronic_conditions=reg.get("chronic_conditions", []),
            emergency_contact_name=reg["emergency_contact_name"],
            emergency_contact_phone=reg["emergency_contact_phone"],
        ))
    except ValueError as e:
        return templates.TemplateResponse(request, "auth/login.html",
            {"partial": "auth/_register_step3.html", "error": str(e)})

    save_pin(pin1)
    request.session.pop("reg_data", None)
    request.session["authenticated"] = True
    return RedirectResponse(url="/chat", status_code=303)


@router.get("/auth/logout", include_in_schema=False)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=303)
