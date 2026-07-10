# DOCMINDER/utils/config.py

import os
import torch
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file or environment variables.")

# --- Knowledge Base Configuration ---
LOCAL_DATA_PATH = "data"  # Folder for your legal documents (PDFs, TXT)

# --- Weaviate Configuration ---
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY") # Not needed for local Docker setup
WEAVIATE_CLASS_NAME = "LegalDocumentChunk" # The name of your data collection in Weaviate

# --- Embedding Model Configuration ---
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# --- Chunking Configuration ---
CHUNK_SIZE = 750
CHUNK_OVERLAP = 150
LEGAL_SEPARATORS = [
    "\n\nCHAPTER ", "\n\nSection ", "\n\nArticle ", "\n\nPart ", "\n\nRule ",
    "\n\nA.", "\n\nB.", "\n\nC.", "\n\nD.", "\n\nE.",
    "\n✓ ", "\n- ", "\n\n", "\n", ". ", " ",
]

# --- Retrieval & Reranking Configuration ---
INITIAL_SEMANTIC_K = 10
INITIAL_KEYWORD_K = 10
RERANKER_TOP_K_CANDIDATES = 20
FINAL_TOP_N_DOCS = 3
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"

# --- LLM Configuration (Gemini) ---
GEMINI_MODEL_NAME = "gemini-1.5-pro"

# --- Prompt Template ---
RAG_PROMPT_TEMPLATE = """
You are a highly specialized legal assistant. Your primary task is to provide accurate, concise, and professional answers
based ONLY on the provided legal context.
- If the answer is not explicitly found within the context, state clearly:
  "I cannot find the answer to this specific question in the provided legal documents."
- Do not invent information or use outside knowledge.
- ALWAYS cite the "act_name" and if available, the "main_point" or "rule_reference" or "section_number" or "chapter_name" from the source document.
  For example: (Trade Marks Rules 2017 SOP, Point C, rule 124) or (Motor Vehicles Act, 1988, Section 3)
- Ensure your citations are precise and directly link to the facts.

Context:
{context}

Question: {input}

Answer:
"""
