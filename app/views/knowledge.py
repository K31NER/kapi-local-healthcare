import requests
import streamlit as st

from api_client import api_upload_document

TIPOS = ["oficial", "personal", "externo"]
CATEGORIAS = ["informe_medico", "guia_clinica", "protocolo", "referencia", "otro"]
SUBTIPOS = ["guia", "resumen", "caso_clinico", "articulo", "otro"]


def render():
    st.subheader(":material/upload_file: Base de Conocimientos")

    with st.container(border=True):
        st.markdown(
            "Sube documentos PDF para **ampliar la base de conocimientos local** de Kapi. "
            "El agente podrá usar este material en futuras consultas como contexto adicional."
        )

    st.markdown("#### Subir documento")

    uploaded = st.file_uploader(
        "Selecciona un archivo PDF",
        type=["pdf"],
        accept_multiple_files=False,
        help="Solo se aceptan archivos PDF.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        tipo = st.selectbox("Tipo", TIPOS, index=0)
    with col2:
        categoria = st.selectbox("Categoría", CATEGORIAS, index=0)
    with col3:
        subtipo = st.selectbox("Subtipo", SUBTIPOS, index=0)

    if st.button(
        "Indexar documento",
        icon=":material/cloud_upload:",
        disabled=uploaded is None,
        type="primary",
    ):
        if uploaded is not None:
            with st.spinner("Indexando documento, esto puede tardar unos segundos…"):
                try:
                    result = api_upload_document(
                        file_bytes=uploaded.read(),
                        filename=uploaded.name,
                        tipo=tipo,
                        categoria=categoria,
                        subtipo=subtipo,
                    )
                    st.success(f"Documento indexado correctamente: `{result.get('path', uploaded.name)}`")
                except requests.ConnectionError:
                    st.error("No se puede conectar al servidor.")
                except requests.HTTPError as e:
                    detail = ""
                    try:
                        detail = e.response.json().get("detail", "")
                    except Exception:
                        pass
                    st.error(f"Error al indexar: {detail or e}")
                except Exception as e:
                    st.error(str(e))

    st.caption(
        "Los documentos se guardan en `Infrastructure/Agents/knowledge/docs/` "
        "y se indexan en la colección vectorial local."
    )
