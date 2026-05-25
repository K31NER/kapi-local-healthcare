from agno.models.ollama import Ollama
from agno.models.llama_cpp import LlamaCpp
from AI_server.llama_server import LLM_BASE_URL,LLM_API_KEY

# Modelo cuantizado
llm_model_llama = LlamaCpp(
    id="gemma4-e2b-q4km",
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY,
    temperature=0.1,
    max_tokens=2048,
    top_p=0.9,
)

llm_model_ollama = Ollama(
    id="gemma4:e2b",
    options={"temperature": 0.3,},
    request_params={"think": False,},
)