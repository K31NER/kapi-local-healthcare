import uuid
import streamlit as st
from styles import CSS
from pathlib import Path
from auth import require_auth
from views import chat as chat_view
from views import profile as profile_view
from views import report as report_view
from views import settings as settings_view
from views import knowledge as knowledge_view

LOGO_PATH = Path(__file__).parent.parent / "media" / "logo.png"

PAGES = {
    ":material/forum: Consulta": chat_view,
    ":material/manage_accounts: Mi Perfil": profile_view,
    ":material/picture_as_pdf: Exportar Informe": report_view,
    ":material/upload_file: Base de Conocimientos": knowledge_view,
    ":material/settings: Configuración": settings_view,
}

st.set_page_config(
    page_title="Kapi — Asistente Médico",
    page_icon=":material/health_and_safety:",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CSS, unsafe_allow_html=True)

# ─── Autenticación ─────────────────────────────────────────────────────────────

if not require_auth():
    st.stop()

# ─── Session state ─────────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_structured" not in st.session_state:
    st.session_state.last_structured = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=130)
    else:
        st.markdown("## Kapi")

    st.markdown("**Kapi**")
    st.caption("Asistente médico · offline & privado")
    st.divider()

    page = st.radio(
        "Navegación",
        list(PAGES.keys()),
        label_visibility="collapsed",
    )

    st.divider()
    st.caption(
        "Kapi es una herramienta de apoyo. "
        "No reemplaza la consulta con un profesional de la salud."
    )

# ─── Routing ─

PAGES[page].render()
