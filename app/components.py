import streamlit as st


def urgency_badge(urgency: str) -> str:
    u = urgency.lower() if urgency else ""
    if u == "high":
        return '<span class="badge-high">URGENTE</span>'
    if u in ("medium", "moderate", "medio"):
        return '<span class="badge-med">MODERADO</span>'
    return '<span class="badge-low">LEVE</span>'


def show_structured(s: dict):
    urgency = (s.get("summary") or {}).get("urgency", "")
    if urgency:
        st.markdown(urgency_badge(urgency), unsafe_allow_html=True)

    if s.get("steps"):
        with st.expander(":material/checklist: Pasos recomendados"):
            for i, step in enumerate(s["steps"], 1):
                st.markdown(f"**{i}.** {step}")

    if s.get("summary"):
        with st.expander(":material/summarize: Resumen clínico"):
            for k, v in s["summary"].items():
                st.markdown(f"**{k}:** {v}")
