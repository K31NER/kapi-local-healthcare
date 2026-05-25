from fpdf import FPDF
from Repositories.user_repository import UserRepository
from Repositories.consultation_repository import ConsultationRepository


def _sanitize(text: str) -> str:
    """Convierte texto a Latin-1 reemplazando caracteres no soportados por Helvetica."""
    if not isinstance(text, str):
        text = str(text)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ExportPDF:
    def __init__(self, user_repo: UserRepository, consult_repo: ConsultationRepository):
        self.user_repo = user_repo
        self.consult_repo = consult_repo

    def execute(self) -> bytes:
        user = self.user_repo.get()
        consultations = self.consult_repo.get_all()

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "Kapi - Historial Medico del Paciente", ln=True, align="C")
        pdf.ln(3)

        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Perfil del Paciente", ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        if user:
            pdf.set_font("Helvetica", "", 11)
            pdf.cell(0, 7, _sanitize(f"Nombre: {user.full_name}"), ln=True)
            pdf.cell(0, 7, _sanitize(f"Fecha de nacimiento: {user.birth_date}"), ln=True)
            pdf.cell(0, 7, _sanitize(f"Genero: {user.gender}"), ln=True)
            pdf.cell(0, 7, _sanitize(f"Tipo de sangre: {user.blood_type}"), ln=True)
            alergias = ", ".join(user.allergies) if user.allergies else "Ninguna"
            pdf.cell(0, 7, _sanitize(f"Alergias: {alergias}"), ln=True)
            condiciones = ", ".join(user.chronic_conditions) if user.chronic_conditions else "Ninguna"
            pdf.cell(0, 7, _sanitize(f"Enfermedades cronicas: {condiciones}"), ln=True)
            pdf.cell(
                0, 7,
                _sanitize(f"Contacto de emergencia: {user.emergency_contact_name} - {user.emergency_contact_phone}"),
                ln=True,
            )
        else:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 7, "No hay perfil registrado.", ln=True)

        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, _sanitize(f"Historial de Consultas ({len(consultations)} registros)"), ln=True)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        if not consultations:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 7, "No hay consultas registradas.", ln=True)

        for i, c in enumerate(consultations, 1):
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(
                0, 7,
                _sanitize(f"[{c.created_at.strftime('%Y-%m-%d %H:%M')}]  Consulta #{i}"),
                ln=True,
            )
            pdf.set_font("Helvetica", "", 10)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, _sanitize(f"Pregunta: {c.question}"))
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, _sanitize(f"Respuesta: {c.answer}"))
            if c.steps:
                pdf.set_x(pdf.l_margin)
                pdf.cell(0, 6, "Pasos recomendados:", ln=True)
                for j, step in enumerate(c.steps, 1):
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 6, _sanitize(f"  {j}. {step}"))
            if c.summary:
                summary_str = " | ".join(f"{k}={v}" for k, v in c.summary.items())
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 6, _sanitize(f"Resumen: {summary_str}"))
            pdf.ln(3)

        return bytes(pdf.output())
