# DOCMINDER/utils/ingestion_service.py

from typing import List

from .config import LOCAL_DATA_PATH
from .database import get_weaviate_client, clear_weaviate_schema
from .document_loader import load_documents, load_document_files
from .chunking_service import chunk_documents
from .embedding_service import initialize_embeddings
from .persistence_service import get_vector_store


def ingest_documents(file_paths: List[str], client, vector_store) -> int:
    """Load, chunk, and persist documents from an explicit list of file paths.

    Returns the number of chunks added.  Does *not* clear the schema —
    callers decide whether to wipe the collection first.
    """
    # 1. Load documents from given file paths
    documents = load_document_files(file_paths)
    if not documents:
        print("No documents loaded. Skipping ingestion.")
        return 0

    # 2. Chunk documents
    chunks = chunk_documents(documents)
    if not chunks:
        print("No chunks were created. Skipping ingestion.")
        return 0

    # 3. Add chunks to Weaviate
    print("Adding document chunks to Weaviate...")
    vector_store.add_documents(chunks)
    print(f"Added {len(chunks)} chunks to Weaviate.")
    return len(chunks)


def run_ingestion():
    """Orchestrates the entire data ingestion pipeline (CLI / ingest.py path).

    Clears the existing collection, loads all documents from LOCAL_DATA_PATH,
    and re-indexes them.
    """
    print("\n--- Starting Data Ingestion Pipeline ---")

    # 1. Clear existing data for a fresh start
    try:
        clear_weaviate_schema()
    except Exception as e:
        print(f"Could not clear schema. Please ensure Weaviate is running. Aborting. Error: {e}")
        return

    # 2. Collect file paths from LOCAL_DATA_PATH
    import os
    if not os.path.exists(LOCAL_DATA_PATH):
        os.makedirs(LOCAL_DATA_PATH)
        print(f"Created data folder: '{LOCAL_DATA_PATH}'. Please add documents there.")
        return

    file_paths = [
        os.path.join(LOCAL_DATA_PATH, f)
        for f in os.listdir(LOCAL_DATA_PATH)
        if f.lower().endswith((".pdf", ".txt"))
    ]
    if not file_paths:
        print("No documents found. Ingestion pipeline stopped.")
        return

    # 3. Initialize embeddings, client, and vector store
    embeddings = initialize_embeddings()
    client = get_weaviate_client()
    vector_store = get_vector_store(client, embeddings)

    # 4. Ingest
    ingest_documents(file_paths, client, vector_store)
    print("--- Data Ingestion Pipeline Complete ---")
