import uuid
import requests
import streamlit as st
from api_client import iter_chat_events
from components import show_structured


def _stream_response(question: str, session_id: str) -> str:
    """
    Muestra el proceso de pensamiento mientras el agente responde,
    luego transmite la respuesta token a token.
    Retorna el texto completo de la respuesta.
    """
    thinking_ph = st.empty()
    response_ph = st.empty()
    full_text = ""
    has_content = False

    for event_type, data in iter_chat_events(question, session_id):
        if event_type == "thinking":
            if not has_content:
                thinking_ph.caption(f":material/psychology: {data['text']}")
        elif event_type == "content":
            if not has_content:
                thinking_ph.empty()
                has_content = True
            full_text += data["text"]
            response_ph.markdown(full_text + "▌")
        elif event_type == "done":
            st.session_state.last_structured = data
        elif event_type == "error":
            thinking_ph.empty()
            st.error(f"Error del agente: {data['error']}")

    response_ph.markdown(full_text)
    return full_text


def render():
    col_title, col_btn = st.columns([8, 2])
    with col_title:
        st.subheader(":material/forum: Consulta Médica")
        st.caption("Describe tus síntomas con detalle. El agente recuerda el contexto de la sesión.")
    with col_btn:
        st.write("")
        if st.button("Nueva sesión", icon=":material/refresh:", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.last_structured = None
            st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("structured"):
                show_structured(msg["structured"])

    if question := st.chat_input("Ej: Tengo fiebre de 38°C y dolor de garganta desde ayer…"):
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            try:
                st.session_state.last_structured = None
                response_text = _stream_response(question, st.session_state.session_id)
                structured = st.session_state.last_structured
                if structured:
                    show_structured(structured)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text or "",
                    "structured": structured,
                })

            except requests.ConnectionError:
                st.error("No se puede conectar al servidor. Verifica que la API esté corriendo.")
            except requests.HTTPError as e:
                st.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
            except Exception as e:
                st.error(f"Error inesperado: {e}")
