from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from Config.settings import settings
from agno.skills import Skills, LocalSkills
from Infrastructure.Agents.knowledge.docs import knowledge_db
from Infrastructure.Agents.schemas.agent import ResponseModel
from Infrastructure.Agents.llm import llm_model_llama,llm_model_ollama
from Infrastructure.Agents.prompt import REDACTER_AGENT_PROMPT, CONSULT_AGENT_PROMPT

# Definimos el llm en base al modo
llm_model = llm_model_llama if settings.MODE == "llama" else llm_model_ollama

agent_db = SqliteDb(
    db_url=settings.DB_URI,
    session_table="sessions",
    memory_table="memory",
)

consult_agent = Agent(
    name="Consult Agent",
    description="Agente que procesa la consulta del usuario",
    model=llm_model,
    instructions=CONSULT_AGENT_PROMPT,
    skills=Skills(loaders=[LocalSkills("Infrastructure/Agents/skills")]),
    # Activamos la base de datos
    db=agent_db,
    add_history_to_context=True,
    read_chat_history=True,
    update_memory_on_run=True,
    enable_user_memories=True,
    add_memories_to_context=True,
    enable_session_summaries=True,        # genera el resumen
    add_session_summary_to_context=False, 
    # Activamos el RAG
    knowledge=knowledge_db,
    search_knowledge=False,
    add_knowledge_to_context=True,
    enable_agentic_knowledge_filters=False,
    debug_mode=True,
    debug_level=2
)

redacter_agent = Agent(
    name="Redacter agent",
    description="Agente encargado de realizar el informe medico y transformarlo al ResponseModel",
    model=llm_model,
    instructions=REDACTER_AGENT_PROMPT,
    output_schema=ResponseModel,
    #debug_mode=True
)
