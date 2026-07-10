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

# --- CRITICAL: CONFIGURE PATH TO POPPLER ---
# Replace this placeholder with the full path to your Poppler 'bin' directory.
# Example for Windows: r'C:\poppler-23.11.0\Library\bin'
POPPLER_PATH = r'C:\Program Files\poppler-25.07.0\Library\bin'

def _ocr_page(pdf_path: str, page_num: int) -> str:
    """Performs OCR on a single page of a PDF."""
    if not all([pytesseract, convert_from_path, POPPLER_PATH]):
        if not POPPLER_PATH:
            print("WARNING: POPPLER_PATH is not set in document_loader.py. OCR will be skipped.")
        return ""
    try:
        images = convert_from_path(
            pdf_path,
            first_page=page_num + 1,
            last_page=page_num + 1,
            poppler_path=POPPLER_PATH
        )
        if images:
            return pytesseract.image_to_string(images[0])
        return ""
    except Exception as e:
        print(f"    ERROR: OCR failed for page {page_num + 1} of '{os.path.basename(pdf_path)}'. Reason: {e}")
        return ""

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
            try:
                loader = PyPDFLoader(filepath)
                pdf_pages = loader.load()
                processed_pages = []
                for i, page in enumerate(pdf_pages):
                    if not page.page_content.strip():
                        print(f"  - Page {i+1} of '{filename}' is empty, attempting OCR...")
                        ocr_text = _ocr_page(filepath, i)
                        if ocr_text.strip():
                            page.page_content = ocr_text
                            print(f"    SUCCESS: OCR extracted text from page {i+1}.")
                    processed_pages.append(page)
                docs.extend(processed_pages)
                print(f"  SUCCESS: Loaded '{filename}'.")
            except Exception as e:
                print(f"  ERROR: Failed to load PDF '{filename}'. Reason: {e}")
        elif filename.lower().endswith(".txt"):
            try:
                loader = TextLoader(filepath)
                docs.extend(loader.load())
                print(f"  SUCCESS: Loaded '{filename}'.")
            except Exception as e:
                print(f"  ERROR: Failed to load TXT '{filename}'. Reason: {e}")

    print(f"Total documents loaded: {len(docs)}")
    return docs
