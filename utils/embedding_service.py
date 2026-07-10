# DOCMINDER/utils/embedding_service.py

from langchain_community.embeddings import HuggingFaceEmbeddings
from .config import EMBEDDING_MODEL_NAME, DEVICE

def initialize_embeddings():
    """Initializes and returns the HuggingFace embeddings model."""
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME} on device: {DEVICE}...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": DEVICE}
    )
    print("Embedding model loaded.")
    return embeddings
