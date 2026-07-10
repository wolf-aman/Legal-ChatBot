# DOCMINDER/utils/chunking_service.py

import os
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from .config import CHUNK_SIZE, CHUNK_OVERLAP, LEGAL_SEPARATORS
from .annotation_rules import extract_legal_metadata

def chunk_documents(documents: List[Document]) -> List[Document]:
    """Splits documents and annotates them with legal metadata."""
    if not documents:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=LEGAL_SEPARATORS,
    )

    all_chunks = []
    for doc in documents:
        split_texts = text_splitter.split_text(doc.page_content)
        for i, text in enumerate(split_texts):
            chunk_metadata = extract_legal_metadata(text, doc.metadata.get("source", "unknown"))
            chunk_metadata["chunk_id"] = f"{os.path.basename(doc.metadata.get('source', ''))}_chunk_{i}"
            all_chunks.append(Document(page_content=text, metadata=chunk_metadata))

    print(f"Created {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks
