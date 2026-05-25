import requests
import streamlit as st

from api_client import api_export_pdf


def render():
    st.subheader(":material/picture_as_pdf: Exportar Informe Médico")

    with st.container(border=True):
        st.markdown(
            "El informe PDF incluye el **perfil del paciente**, el **historial de consultas** "
            "y los **resúmenes clínicos** generados por el agente. "
            "El médico puede usar este documento para evaluar el estado del paciente."
        )

    if st.button("Descargar PDF", icon=":material/download:"):
        try:
            pdf_bytes = api_export_pdf()
            st.download_button(
                label="Guardar kapi_historial.pdf",
                data=pdf_bytes,
                file_name="kapi_historial.pdf",
                mime="application/pdf",
                icon=":material/save:",
            )
            st.success("PDF generado. Haz clic en Guardar para descargarlo.")
        except requests.ConnectionError:
            st.error("No se puede conectar al servidor.")
        except requests.HTTPError as e:
            st.error(f"Error al generar el PDF: {e}")
        except Exception as e:
            st.error(str(e))

    st.caption("El PDF se genera en el momento con los datos actuales de la base de datos local.")
