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
        source = os.path.basename(doc.metadata.get("source", "unknown"))
        page = doc.metadata.get("page", 0)  # PyPDFLoader sets this, 0-indexed
        doc_header_text = doc.metadata.get("doc_header_text", "")

        split_texts = text_splitter.split_text(doc.page_content)
        for i, text in enumerate(split_texts):
            chunk_metadata = extract_legal_metadata(
                text,
                doc.metadata.get("source", "unknown"),
                doc_header_text=doc_header_text,
                page=page + 1,
            )
            chunk_metadata["chunk_id"] = f"{source}_p{page + 1}_chunk_{i}"
            chunk_metadata["page"] = page + 1  # 1-indexed for human display
            all_chunks.append(Document(page_content=text, metadata=chunk_metadata))

    print(f"Created {len(all_chunks)} chunks from {len(documents)} documents.")
    return all_chunks
