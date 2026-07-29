# DOCMINDER/utils/llm_service.py

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME, RAG_PROMPT_TEMPLATE

def initialize_llm():
    """Initializes the Gemini Chat Model with automatic retry on transient failures."""
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=0,
        convert_system_message_to_human=True,
        max_retries=2
    )

def get_rag_prompt():
    """Returns the RAG prompt template."""
    return ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
