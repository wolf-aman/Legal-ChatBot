# DOCMINDER/utils/ingestion_service.py

from .config import LOCAL_DATA_PATH
from .database import get_weaviate_client, clear_weaviate_schema
from .document_loader import load_documents
from .chunking_service import chunk_documents
from .embedding_service import initialize_embeddings
from .persistence_service import get_vector_store

def run_ingestion():
    """Orchestrates the entire data ingestion pipeline."""
    print("\n--- Starting Data Ingestion Pipeline ---")

    # 1. Clear existing data for a fresh start
    try:
        clear_weaviate_schema()
    except Exception as e:
        print(f"Could not clear schema. Please ensure Weaviate is running. Aborting. Error: {e}")
        return

    # 2. Load documents
    documents = load_documents(LOCAL_DATA_PATH)
    if not documents:
        print("No documents found. Ingestion pipeline stopped.")
        return

    # 3. Chunk documents
    chunks = chunk_documents(documents)
    if not chunks:
        print("No chunks were created. Ingestion pipeline stopped.")
        return

    # 4. Initialize embeddings
    embeddings = initialize_embeddings()

    # 5. Get Weaviate client and vector store instance
    client = get_weaviate_client()
    vector_store = get_vector_store(client, embeddings)

    # 6. Add documents to Weaviate
    print("Adding document chunks to Weaviate...")
    vector_store.add_documents(chunks)
    print("--- Data Ingestion Pipeline Complete ---")
