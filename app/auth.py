import re
import requests
import streamlit as st
from pathlib import Path
from datetime import date


_PIN_FILE = Path(__file__).parent.parent / ".kapi_pin"
_API_URL  = "http://localhost:8000"
_LOGO     = Path(__file__).parent.parent / "media" / "logo.png"

_BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
_GENDERS     = ["M", "F", "Otro"]

_COMMON_ALLERGIES = [
    "Penicilina", "Amoxicilina", "Ibuprofeno", "Aspirina", "Naproxeno",
    "Látex", "Mariscos", "Nueces", "Maní", "Leche", "Huevo",
    "Gluten", "Soya", "Polen", "Ácaros", "Pelo de mascota",
]

_COMMON_CONDITIONS = [
    "Diabetes tipo 1", "Diabetes tipo 2", "Hipertensión", "Hipotensión",
    "Asma", "EPOC", "Hipotiroidismo", "Hipertiroidismo",
    "Artritis reumatoide", "Osteoporosis", "Epilepsia",
    "Anemia", "Insuficiencia renal", "Enfermedad cardíaca",
]


# ── PIN helpers ───────────────────────────────────────────────────────────────

def is_registered() -> bool:
    return _PIN_FILE.exists()

def save_pin(pin: str) -> None:
    _PIN_FILE.write_text(pin.strip(), encoding="utf-8")

def check_pin(pin: str) -> bool:
    return _PIN_FILE.exists() and _PIN_FILE.read_text(encoding="utf-8").strip() == pin.strip()

def delete_credentials() -> None:
    if _PIN_FILE.exists():
        _PIN_FILE.unlink()


# ── Teléfono ──────────────────────────────────────────────────────────────────

def _format_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"+{digits[0]} ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
    if len(digits) > 11:
        return f"+{digits[:2]} {digits[2:5]} {digits[5:8]} {digits[8:]}"
    return raw


# ── Columna de branding ───────────────────────────────────────────────────────

def _render_branding(col):
    with col:
        st.write("")

        if _LOGO.exists():
            _, c, _ = st.columns([1, 3, 1])
            with c:
                st.image(str(_LOGO), use_container_width=True)

        st.markdown(
            "<div style='text-align:center; padding-top:1rem;'>"
            "  <div style='font-size:1.6rem; font-weight:700; margin-bottom:0.25rem;'>Kapi</div>"
            "  <div style='color:#555; font-size:0.9rem;'>Asistente Médico Local</div>"
            "  <div style='color:#888; font-size:0.8rem; margin-top:0.4rem;'>"
            "    Offline &nbsp;·&nbsp; Privado &nbsp;·&nbsp; Para ti"
            "  </div>"
            "</div>",
            unsafe_allow_html=True,
        )


# ── Indicador de paso ─────────────────────────────────────────────────────────

def _step_indicator(current: int):
    steps = ["① Info básica", "② Salud y contacto", "③ PIN"]
    parts = []
    for i, label in enumerate(steps, 1):
        if i < current:
            style = "text-decoration:line-through; color:#bbb;"
        elif i == current:
            style = "font-weight:700; color:#1A1A2E;"
        else:
            style = "color:#aaa;"
        parts.append(f"<span style='{style}'>{label}</span>")
    st.markdown(
        "<div style='font-size:0.8rem; margin-bottom:0.8rem;'>"
        + " &nbsp;→&nbsp; ".join(parts)
        + "</div>",
        unsafe_allow_html=True,
    )


def _nav_buttons(back_label="Volver", next_label="Continuar", last=False):
    cb, cs = st.columns(2)
    back = cb.form_submit_button(back_label, icon=":material/arrow_back:", use_container_width=True)
    icon = ":material/how_to_reg:" if last else ":material/arrow_forward:"
    fwd  = cs.form_submit_button(next_label, icon=icon, use_container_width=True)
    return back, fwd


# ── Paso 1: Info básica ───────────────────────────────────────────────────────

def _render_step1(col):
    with col:
        st.markdown("### Crear tu perfil")
        _step_indicator(1)

        with st.form("reg_step1"):
            full_name = st.text_input("Nombre completo *", placeholder="Ej: María García")
            c1, c2 = st.columns(2)
            birth_date = c1.date_input(
                "Fecha de nacimiento *",
                value=date(1990, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today(),
                format="YYYY-MM-DD",
            )
            gender = c2.selectbox("Género *", _GENDERS)
            c3, c4 = st.columns(2)
            blood_type = c3.selectbox("Tipo de sangre *", _BLOOD_TYPES)
            c4.write("")  # alinea la segunda columna

            submitted = st.form_submit_button(
                "Continuar", icon=":material/arrow_forward:", use_container_width=True
            )

        if submitted:
            if not full_name:
                st.error("El nombre completo es obligatorio.")
            else:
                st.session_state.reg_data = {
                    "full_name": full_name,
                    "birth_date": birth_date.isoformat(),
                    "gender": gender,
                    "blood_type": blood_type,
                }
                st.session_state.reg_step = 2
                st.rerun()


# ── Paso 2: Salud y contacto de emergencia ────────────────────────────────────

def _render_step2(col):
    with col:
        st.markdown("### Salud y contacto")
        _step_indicator(2)

        with st.form("reg_step2"):
            allergies = st.multiselect(
                "Alergias",
                options=_COMMON_ALLERGIES,
                placeholder="Selecciona o escribe para buscar…",
                accept_new_options=True,
            )
            chronic = st.multiselect(
                "Enfermedades crónicas",
                options=_COMMON_CONDITIONS,
                placeholder="Selecciona o escribe para buscar…",
                accept_new_options=True,
            )
            c1, c2 = st.columns(2)
            ec_name      = c1.text_input("Contacto de emergencia *", placeholder="Juan García")
            ec_phone_raw = c2.text_input(
                "Teléfono *",
                placeholder="+57 300 123 4567",
                help="Incluye código de país. Ej: +57 300 123 4567",
            )
            back, fwd = _nav_buttons()

        if back:
            st.session_state.reg_step = 1
            st.rerun()

        if fwd:
            if not all([ec_name, ec_phone_raw]):
                st.error("El contacto de emergencia y su teléfono son obligatorios.")
            else:
                st.session_state.reg_data.update({
                    "allergies": list(allergies),
                    "chronic_conditions": list(chronic),
                    "emergency_contact_name": ec_name,
                    "emergency_contact_phone": _format_phone(ec_phone_raw),
                })
                st.session_state.reg_step = 3
                st.rerun()


# ── Paso 3: PIN ───────────────────────────────────────────────────────────────

def _render_step3(col):
    with col:
        st.markdown("### PIN de acceso")
        _step_indicator(3)

        with st.form("reg_step3"):
            pin1 = st.text_input("PIN (mínimo 4 caracteres) *", type="password")
            pin2 = st.text_input("Confirmar PIN *", type="password")
            back, create = _nav_buttons(next_label="Crear cuenta", last=True)

        if back:
            st.session_state.reg_step = 2
            st.rerun()

        if create:
            if len(pin1) < 4:
                st.error("El PIN debe tener al menos 4 caracteres.")
            elif pin1 != pin2:
                st.error("Los PINs no coinciden.")
            else:
                try:
                    r = requests.post(
                        f"{_API_URL}/user", json=st.session_state.reg_data, timeout=5
                    )
                    r.raise_for_status()
                    save_pin(pin1)
                    for k in ("reg_step", "reg_data"):
                        st.session_state.pop(k, None)
                    st.session_state.authenticated = True
                    st.rerun()
                except requests.ConnectionError:
                    st.error("No se puede conectar al servidor.")
                except requests.HTTPError as e:
                    st.error(f"Error: {e.response.json().get('detail', e)}")


# ── Pantalla de login ─────────────────────────────────────────────────────────

def _render_login(col):
    with col:
        st.write("")
        st.markdown("### Bienvenido de vuelta")
        st.caption("Ingresa tu PIN para continuar.")
        st.write("")

        with st.form("login_form"):
            pin = st.text_input("PIN de acceso", type="password", placeholder="••••")
            submitted = st.form_submit_button(
                "Ingresar", icon=":material/login:", use_container_width=True
            )

        if submitted:
            if check_pin(pin):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("PIN incorrecto.")


# ── Punto de entrada ──────────────────────────────────────────────────────────

def require_auth() -> bool:
    if st.session_state.get("authenticated"):
        return True

    _, center, _ = st.columns([2, 7, 2])
    with center:
        with st.container(border=True):
            col_brand, col_form = st.columns([1, 1], gap="large")
            _render_branding(col_brand)

            if is_registered():
                _render_login(col_form)
            else:
                if "reg_step" not in st.session_state:
                    st.session_state.reg_step = 1

                step = st.session_state.reg_step
                if step == 1:
                    _render_step1(col_form)
                elif step == 2:
                    _render_step2(col_form)
                else:
                    _render_step3(col_form)

    return False
