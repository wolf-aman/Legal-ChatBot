# DOCMINDER/utils/rag_service.py

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

def create_rag_chain(llm, prompt, retriever):
    """Constructs the complete RAG chain."""
    document_chain = create_stuff_documents_chain(llm, prompt)
    return create_retrieval_chain(retriever, document_chain)
