# DOCMINDER/utils/document_loader.py

import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document

# --- OCR Imports ---
try:
    from PIL import Image
    from pdf2image import convert_from_path
    import pytesseract
except ImportError:
    print("WARNING: OCR libraries (pytesseract, pdf2image, Pillow) not found. Scanned PDFs will be skipped.")
    Image = None
    convert_from_path = None
    pytesseract = None

# --- Poppler path: read from environment variable (None = use system PATH) ---
POPPLER_PATH = os.getenv("POPPLER_PATH") or None


def _ocr_page(pdf_path: str, page_num: int) -> str:
    """Performs OCR on a single page of a PDF."""
    if not all([pytesseract, convert_from_path]):
        return ""
    try:
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,
            last_page=page_num + 1,
            poppler_path=POPPLER_PATH  # None = use system PATH (Linux/Mac default)
        )
        if images:
            return pytesseract.image_to_string(images[0])
        return ""
    except Exception as e:
        print(f"    ERROR: OCR failed for page {page_num + 1} of '{os.path.basename(pdf_path)}'. Reason: {e}")
        return ""


def _load_single_pdf(filepath: str) -> List[Document]:
    """Loads a single PDF, applies OCR to blank pages, and caches first-page text."""
    filename = os.path.basename(filepath)
    try:
        loader = PyPDFLoader(filepath)
        pdf_pages = loader.load()

        # Cache first-page text for act-name regex (Fix #3)
        first_page_text = pdf_pages[0].page_content if pdf_pages else ""

        processed_pages = []
        for i, page in enumerate(pdf_pages):
            if not page.page_content.strip():
                print(f"  - Page {i+1} of '{filename}' is empty, attempting OCR...")
                ocr_text = _ocr_page(filepath, i)
                if ocr_text.strip():
                    page.page_content = ocr_text
                    print(f"    SUCCESS: OCR extracted text from page {i+1}.")

            # Attach doc_header_text to every page's metadata
            page.metadata["doc_header_text"] = first_page_text
            processed_pages.append(page)

        print(f"  SUCCESS: Loaded '{filename}'.")
        return processed_pages
    except Exception as e:
        print(f"  ERROR: Failed to load PDF '{filename}'. Reason: {e}")
        return []


def _load_single_txt(filepath: str) -> List[Document]:
    """Loads a single TXT file."""
    filename = os.path.basename(filepath)
    try:
        loader = TextLoader(filepath)
        docs = loader.load()
        print(f"  SUCCESS: Loaded '{filename}'.")
        return docs
    except Exception as e:
        print(f"  ERROR: Failed to load TXT '{filename}'. Reason: {e}")
        return []


def load_documents(path: str) -> List[Document]:
    """Loads all PDF and TXT documents from a folder, with OCR for scanned PDFs."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created data folder: '{path}'. Please add your documents there.")
        return []

    print(f"Loading documents from: '{path}'")
    docs = []
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if filename.lower().endswith(".pdf"):
            docs.extend(_load_single_pdf(filepath))
        elif filename.lower().endswith(".txt"):
            docs.extend(_load_single_txt(filepath))

    print(f"Total documents loaded: {len(docs)}")
    return docs


def load_document_files(file_paths: List[str]) -> List[Document]:
    """Loads documents from an explicit list of file paths (for Streamlit uploads)."""
    docs = []
    for filepath in file_paths:
        if filepath.lower().endswith(".pdf"):
            docs.extend(_load_single_pdf(filepath))
        elif filepath.lower().endswith(".txt"):
            docs.extend(_load_single_txt(filepath))
        else:
            print(f"  SKIPPED: Unsupported file type '{os.path.basename(filepath)}'")
    print(f"Total documents loaded: {len(docs)}")
    return docs
