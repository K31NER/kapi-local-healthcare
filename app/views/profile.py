import requests
import streamlit as st
from datetime import date, datetime
from api_client import api_get_user, api_save_user, api_delete_user

_BLOOD_TYPES = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
_GENDERS = ["M", "F", "Otro"]

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


def _parse_date(val) -> date:
    if isinstance(val, date):
        return val
    try:
        return datetime.strptime(str(val), "%Y-%m-%d").date()
    except ValueError:
        return date(1990, 1, 1)


def _profile_form(key: str, initial: dict | None = None):
    initial = initial or {}
    with st.form(key):
        full_name = st.text_input("Nombre completo *", value=initial.get("full_name", ""))
        col_a, col_b = st.columns(2)
        birth_date = col_a.date_input(
            "Fecha de nacimiento *",
            value=_parse_date(initial.get("birth_date", date(1990, 1, 1))),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="YYYY-MM-DD",
        )
        gender_idx = _GENDERS.index(initial["gender"]) if initial.get("gender") in _GENDERS else 0
        gender = col_b.selectbox("Género *", _GENDERS, index=gender_idx)

        col_c, col_d = st.columns(2)
        bt_idx = _BLOOD_TYPES.index(initial["blood_type"]) if initial.get("blood_type") in _BLOOD_TYPES else 0
        blood_type = col_c.selectbox("Tipo de sangre *", _BLOOD_TYPES, index=bt_idx)
        col_d.write("")

        allergies = st.multiselect(
            "Alergias",
            options=_COMMON_ALLERGIES,
            default=[a for a in initial.get("allergies", []) if a in _COMMON_ALLERGIES],
            accept_new_options=True,
            placeholder="Selecciona o escribe para buscar…",
        )
        chronic = st.multiselect(
            "Enfermedades crónicas",
            options=_COMMON_CONDITIONS,
            default=[c for c in initial.get("chronic_conditions", []) if c in _COMMON_CONDITIONS],
            accept_new_options=True,
            placeholder="Selecciona o escribe para buscar…",
        )

        col_e, col_f = st.columns(2)
        ec_name = col_e.text_input("Contacto de emergencia *", value=initial.get("emergency_contact_name", ""))
        ec_phone = col_f.text_input("Teléfono de emergencia *", value=initial.get("emergency_contact_phone", ""))

        is_edit = bool(initial)
        icon = ":material/save:" if is_edit else ":material/how_to_reg:"
        label = "Guardar cambios" if is_edit else "Crear perfil"
        submitted = st.form_submit_button(label, icon=icon, use_container_width=True)

    if submitted:
        return {
            "full_name": full_name,
            "birth_date": birth_date.isoformat(),
            "gender": gender,
            "blood_type": blood_type,
            "allergies": list(allergies),
            "chronic_conditions": list(chronic),
            "emergency_contact_name": ec_name,
            "emergency_contact_phone": ec_phone,
        }
    return None


def render():
    st.subheader(":material/manage_accounts: Mi Perfil")

    user = api_get_user()

    if user == "offline":
        st.error("No se puede conectar al servidor.")
        st.stop()

    if user:
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Nombre", user["full_name"])
            c2.metric("Nacimiento", user["birth_date"])
            c3.metric("Género", user["gender"])
            c1.metric("Sangre", user["blood_type"])
            c2.metric("Alergias", ", ".join(user["allergies"]) if user["allergies"] else "Ninguna")
            c3.metric("Contacto emergencia", user["emergency_contact_name"])

        tab_edit, tab_delete = st.tabs([":material/edit: Editar", ":material/delete: Eliminar"])

        with tab_edit:
            st.markdown("#### Actualizar perfil")
            payload = _profile_form("edit_profile_form", initial=user)
            if payload:
                try:
                    api_save_user(payload, editing=True)
                    st.success("Perfil actualizado correctamente.")
                    st.rerun()
                except requests.HTTPError as e:
                    st.error(e.response.json().get("detail", str(e)))

        with tab_delete:
            st.warning("Esta acción eliminará permanentemente tu perfil de la base de datos local.")
            if st.button("Confirmar eliminación", icon=":material/delete_forever:", type="secondary"):
                try:
                    api_delete_user()
                    st.success("Perfil eliminado.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    else:
        st.info("No tienes un perfil registrado. Completa el formulario para comenzar.")
        st.markdown("#### Crear perfil")
        payload = _profile_form("create_profile_form")
        if payload:
            if not all([payload["full_name"], payload["birth_date"],
                        payload["emergency_contact_name"], payload["emergency_contact_phone"]]):
                st.error("Completa todos los campos obligatorios (*).")
            else:
                try:
                    api_save_user(payload, editing=False)
                    st.success("Perfil creado correctamente.")
                    st.rerun()
                except requests.HTTPError as e:
                    st.error(e.response.json().get("detail", str(e)))
