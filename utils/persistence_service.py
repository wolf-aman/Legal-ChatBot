# DOCMINDER/utils/persistence_service.py

from langchain_weaviate.vectorstores import WeaviateVectorStore
from .config import WEAVIATE_CLASS_NAME

def get_vector_store(client, embeddings):
    """Initializes and returns a WeaviateVectorStore instance for later use."""
    return WeaviateVectorStore(
        client=client,
        index_name=WEAVIATE_CLASS_NAME,
        text_key="text",
        embedding=embeddings,
        attributes=["source", "act_name", "section_number", "chapter_name", "rule_reference"]
    )
