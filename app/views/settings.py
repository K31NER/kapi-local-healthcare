import requests
import streamlit as st
from auth import delete_credentials
from api_client import api_export_pdf, api_delete_user


def render():
    st.subheader(":material/settings: Configuración")

    # ── Exportar datos ────────────────────────────────────────────────────────
    st.markdown("#### Exportar mis datos")
    st.caption("Descarga un PDF con tu perfil médico y el historial completo de consultas.")

    if st.button("Descargar todos mis datos (PDF)", icon=":material/download:"):
        try:
            pdf_bytes = api_export_pdf()
            st.download_button(
                label="Guardar kapi_historial.pdf",
                data=pdf_bytes,
                file_name="kapi_historial.pdf",
                mime="application/pdf",
                icon=":material/save:",
            )
        except requests.ConnectionError:
            st.error("No se puede conectar al servidor.")
        except Exception as e:
            st.error(f"Error al generar el PDF: {e}")

    st.divider()

    # ── Borrar todos los datos ────────────────────────────────────────────────
    st.markdown("#### Borrar todos mis datos")
    st.warning(
        "Esta acción elimina permanentemente tu perfil, el historial de consultas "
        "y las credenciales de acceso. Al volver a abrir la app se te pedirá un nuevo registro."
    )

    confirm = st.checkbox("Entiendo que esta acción no se puede deshacer")

    if st.button("Borrar todos mis datos", icon=":material/delete_forever:", disabled=not confirm, type="secondary"):
        try:
            api_delete_user()
        except requests.ConnectionError:
            st.error("No se puede conectar al servidor.")
            st.stop()
        except requests.HTTPError as e:
            if e.response.status_code != 404:
                st.error(f"Error al borrar el perfil: {e}")
                st.stop()

        delete_credentials()

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.success("Todos tus datos han sido eliminados.")
        st.rerun()
