import logging
from typing import Generator
from datetime import datetime
from fastapi import BackgroundTasks
from Domain.consultation import Consultation
from Infrastructure.Agents.schemas.agent import InputModel
from Infrastructure.Agents.prompt import CONSULT_AGENT_PROMPT
from Infrastructure.Agents.agent import consult_agent, redacter_agent
from Repositories.consultation_repository import ConsultationRepository
from Domain.chat import ChatEvent, ThinkingEvent, ContentEvent, ErrorEvent, DoneEvent

_logger = logging.getLogger(__name__)

class LocalKapi:

    def __init__(self, consult, redacter):
        self.consult = consult
        self.redacter = redacter

    def run(self, input: InputModel):
        """Responde de forma síncrona. agno gestiona el RAG internamente."""
        original_instructions = self.consult.instructions
        try:
            contexto_paciente = self._build_patient_context(input)
            self.consult.instructions = f"{CONSULT_AGENT_PROMPT}{contexto_paciente}"
            response = self.consult.run(input.question)
            redacted = self.redacter.run(response.content)
            return redacted.content
        except Exception as e:
            raise RuntimeError(f"Error en el agente: {e}") from e
        finally:
            self.consult.instructions = original_instructions

    def _build_patient_context(self, user_input: InputModel) -> str:
        allergies = (
            ", ".join(user_input.context_user.allergies)
            if user_input.context_user.allergies
            else "Ninguna registrada"
        )
        chronic_conditions = (
            ", ".join(user_input.context_user.chronic_conditions)
            if user_input.context_user.chronic_conditions
            else "Ninguna registrada"
        )
        return (
            "\n\n[INFORMACION RELEVANTE DEL PACIENTE]\n"
            f"Nombre completo: {user_input.context_user.full_name}\n"
            f"Edad: {user_input.context_user.age}\n"
            f"Género: {user_input.context_user.gender}\n"
            f"Tipo de sangre: {user_input.context_user.blood_type}\n"
            f"Alergias: {allergies}\n"
            f"Enfermedades crónicas: {chronic_conditions}\n"
        )

    def run_stream(
        self,
        user_input: InputModel,
        session_id: str,
        user_id: str,
        save_repo: ConsultationRepository,
        background_tasks: BackgroundTasks,
    ) -> Generator[ChatEvent, None, None]:
        """Genera eventos SSE para una consulta médica.

        Emite DoneEvent en cuanto termina el stream del consult_agent.
        El redacter y el guardado en BD se ejecutan en segundo plano via BackgroundTasks.
        """
        # Estado compartido entre el generador interno y la tarea de fondo.
        # Se popula durante el streaming; se lee cuando la tarea de fondo corre.
        state: list[str] = []

        def _stream_generator():
            from agno.agent import RunEvent

            _tool_started = getattr(RunEvent, "tool_call_started", None)
            _reasoning_step = getattr(RunEvent, "reasoning_step", None)
            original_instructions = self.consult.instructions
            contexto_paciente = self._build_patient_context(user_input)
            self.consult.instructions = f"{CONSULT_AGENT_PROMPT}{contexto_paciente}"

            yield ThinkingEvent(text="Analizando tu consulta...")

            full_response = ""
            try:
                stream = self.consult.run(
                    user_input.question,
                    session_id=session_id,
                    stream=True,
                    user_id=user_id,
                )
                for chunk in stream:
                    if chunk.event == RunEvent.run_content and chunk.content:
                        full_response += chunk.content
                        yield ContentEvent(text=chunk.content, session_id=session_id)
                    elif chunk.event == RunEvent.run_error:
                        error_msg = getattr(chunk, "content", "Error desconocido del agente")
                        state.append("")
                        yield ErrorEvent(error=str(error_msg))
                        return
                    elif _tool_started and chunk.event == _tool_started and chunk.content:
                        yield ThinkingEvent(text=f"Consultando: {chunk.content}")
                    elif _reasoning_step and chunk.event == _reasoning_step and chunk.content:
                        yield ThinkingEvent(text=chunk.content)
            except Exception as e:
                state.append("")
                yield ErrorEvent(error=str(e))
                return
            finally:
                self.consult.instructions = original_instructions

            # Emite DoneEvent inmediatamente con la respuesta cruda para liberar al cliente.
            state.append(full_response)
            yield DoneEvent(
                answer=full_response,
                steps=[],
                summary={},
                session_id=session_id,
                status=self._infer_status(full_response),
            )

        def _after_stream():
            full_response = state[0] if state else ""
            if full_response:
                self._background_processing(user_input, full_response, save_repo, session_id)

        # Registra la tarea ANTES de retornar el generador para que FastAPI la capture.
        background_tasks.add_task(_after_stream)
        return _stream_generator()

    def _infer_status(self, text: str) -> str:
        low = text.lower()
        if any(w in low for w in ["crítico", "urgente", "emergencia", "sala de emergencias", "llama al 112", "llama al 911"]):
            return "Crítico"
        if any(w in low for w in ["moderado", "buscar atención", "atención médica", "consultar a un médico", "médico lo antes"]):
            return "Moderado"
        return "Normal"

    def _background_processing(
        self,
        user_input: InputModel,
        full_response: str,
        save_repo: ConsultationRepository,
        session_id: str = "",
    ) -> None:
        """Ejecuta el redacter y guarda la consulta estructurada en la BD."""
        try:
            result = self.redacter.run(full_response)
            structured = result.content if result else None
            steps = (structured.steps if structured else None) or []
            status = (structured.status if structured else None) or "Normal"
            save_repo.save(Consultation(
                question=user_input.question,
                answer=full_response,
                steps=steps,
                status=status,
                session_id=session_id,
                created_at=datetime.now(),
            ))
        except Exception as e:
            _logger.error("Error en background processing: %s", e, exc_info=True)
            try:
                save_repo.save(Consultation(
                    question=user_input.question,
                    answer=full_response,
                    steps=[],
                    status="Normal",
                    session_id=session_id,
                    created_at=datetime.now(),
                ))
            except Exception as save_err:
                _logger.error("Error al guardar consulta de fallback: %s", save_err, exc_info=True)


kapi = LocalKapi(consult_agent, redacter_agent)
