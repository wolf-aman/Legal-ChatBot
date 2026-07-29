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
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200
LEGAL_SEPARATORS = [
    # Section-level boundaries first (tried before character-count splitting)
    "\n\nCHAPTER ", "\n\nPART ",
    "\n\nSection ", "\n\nArticle ", "\n\nRule ",
    # List/point separators
    "\n\nA.", "\n\nB.", "\n\nC.", "\n\nD.", "\n\nE.",
    "\n✓ ", "\n- ",
    # Generic paragraph/line/sentence/word boundaries
    "\n\n", "\n", ". ", " ",
]

# --- Retrieval & Reranking Configuration ---
INITIAL_SEMANTIC_K = 10
HYBRID_ALPHA = 0.5  # 0.0 = pure BM25, 1.0 = pure vector, 0.5 = balanced
FINAL_TOP_N_DOCS = 3
RERANKER_MODEL_NAME = "BAAI/bge-reranker-base"

# --- LLM Configuration (Gemini) ---
GEMINI_MODEL_NAME = "gemini-flash-latest"

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
