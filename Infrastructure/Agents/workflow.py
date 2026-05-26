from typing import Generator
from datetime import datetime
from Domain.consultation import Consultation
from Infrastructure.Agents.schemas.agent import InputModel
from Infrastructure.Agents.prompt import CONSULT_AGENT_PROMPT
from Infrastructure.Agents.agent import consult_agent, redacter_agent
from Repositories.consultation_repository import ConsultationRepository
from Domain.chat import ChatEvent,ThinkingEvent,ContentEvent,ErrorEvent,DoneEvent

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
        allergies = ", ".join(user_input.context_user.allergies) if user_input.context_user.allergies else "Ninguna registrada"
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
    ) -> Generator[ChatEvent, None, None]:
        """Genera eventos SSE para una consulta médica.

        agno gestiona el RAG internamente (knowledge=knowledge_db, search_knowledge=True),
        por lo que la pregunta se pasa directamente al agente sin enriquecimiento manual.
        """
        yield ThinkingEvent(text="Analizando tu consulta...")

        from agno.agent import RunEvent
        import logging

        _logger = logging.getLogger(__name__)
        _tool_started = getattr(RunEvent, "tool_call_started", None)
        _reasoning_step = getattr(RunEvent, "reasoning_step", None)
        original_instructions = self.consult.instructions
        contexto_paciente = self._build_patient_context(user_input)
        self.consult.instructions = f"{CONSULT_AGENT_PROMPT}{contexto_paciente}"
        pregunta_limpia = user_input.question

        full_response = ""
        try:
            stream = self.consult.run(
                pregunta_limpia,
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
                    yield ErrorEvent(error=str(error_msg))
                    return
                elif _tool_started and chunk.event == _tool_started and chunk.content:
                    yield ThinkingEvent(text=f"Consultando: {chunk.content}")
                elif _reasoning_step and chunk.event == _reasoning_step and chunk.content:
                    yield ThinkingEvent(text=chunk.content)
        except Exception as e:
            yield ErrorEvent(error=str(e))
            return
        finally:
            self.consult.instructions = original_instructions

        try:
            result = self.redacter.run(full_response)
            structured = result.content if result else None
            answer = (structured.answer if structured and structured.answer else None) or full_response
            steps = (structured.steps if structured else None) or []
            summary = (structured.summary if structured else None) or {}

            save_repo.save(Consultation(
                question=user_input.question,
                answer=answer,
                steps=steps,
                summary=summary,
                created_at=datetime.now(),
            ))
            yield DoneEvent(answer=answer, steps=steps, summary=summary, session_id=session_id)
        except Exception as e:
            _logger.error("Error en redacter/guardado: %s", e, exc_info=True)
            answer = full_response or "Sin respuesta disponible"
            save_repo.save(Consultation(
                question=user_input.question,
                answer=answer,
                steps=[],
                summary={},
                created_at=datetime.now(),
            ))
            yield DoneEvent(answer=answer, steps=[], summary={}, session_id=session_id)
        


kapi = LocalKapi(consult_agent, redacter_agent)
