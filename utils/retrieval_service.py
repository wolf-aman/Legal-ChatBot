# DOCMINDER/utils/retrieval_service.py

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from .config import RERANKER_MODEL_NAME, FINAL_TOP_N_DOCS, INITIAL_SEMANTIC_K, HYBRID_ALPHA

def setup_retrieval_pipeline(vector_store):
    """Creates a retrieval pipeline with hybrid search and a reranker."""
    print("Setting up retrieval pipeline with hybrid search + reranker...")
    
    # 1. Create the base retriever with Weaviate hybrid search (BM25 + vector)
    # langchain-weaviate 0.0.5 already uses collection.query.hybrid() internally
    # for all searches — the alpha parameter is passed through search_kwargs.
    base_retriever = vector_store.as_retriever(
        search_kwargs={"k": INITIAL_SEMANTIC_K, "alpha": HYBRID_ALPHA}
    )

    # 2. Initialize the CrossEncoder model for reranking
    cross_encoder = HuggingFaceCrossEncoder(model_name=RERANKER_MODEL_NAME)
    
    # 3. Create the reranker compressor
    compressor = CrossEncoderReranker(model=cross_encoder, top_n=FINAL_TOP_N_DOCS)

    # 4. Create the final compression retriever
    # This retriever first gets documents from the base_retriever
    # and then passes them to the compressor for reranking.
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, base_retriever=base_retriever
    )
    
    print("Retrieval pipeline is set up successfully.")
    return compression_retriever
