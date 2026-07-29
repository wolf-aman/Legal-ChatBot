# ⚖️ DOCMINDER — Legal RAG Chatbot

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot purpose-built for legal document analysis. Upload Indian legal documents (PDFs & TXT), ask natural-language questions, and get precise, source-cited answers powered by **Google Gemini** and **Weaviate**.

---

## ✨ Features

- **Intelligent Document Ingestion** — Loads PDFs (including scanned ones via OCR) and TXT files, splits them with legal-aware separators, and enriches every chunk with structured metadata (act name, section number, chapter, rule reference).
- **Hybrid Retrieval + Reranking** — Initial semantic search via Weaviate followed by a CrossEncoder reranker (`BAAI/bge-reranker-base`) to surface the most relevant passages.
- **Google Gemini LLM** — Uses `gemini-flash-latest` with a strict legal-assistant prompt that mandates source citations and refuses to hallucinate.
- **Dual Interface** — Interactive CLI chatbot **and** a polished Streamlit web UI with live document upload, chat history, and formatted source display.
- **RAG Evaluation** — Built-in evaluation script using the [Ragas](https://github.com/explodinggradients/ragas) framework (faithfulness, answer relevancy, context precision & recall).

---

## 🏗️ Architecture

```
User Question
     │
     ▼
┌──────────────┐    ┌──────────────────┐    ┌────────────────────┐
│  Streamlit   │    │  Embedding Model │    │  Weaviate Vector   │
│  / CLI UI    │───▶│  (MiniLM-L6-v2)  │───▶│  Store (Docker)    │
└──────────────┘    └──────────────────┘    └────────┬───────────┘
                                                     │ Top-10 candidates
                                                     ▼
                                            ┌────────────────────┐
                                            │  CrossEncoder      │
                                            │  Reranker (BGE)    │
                                            └────────┬───────────┘
                                                     │ Top-3 documents
                                                     ▼
                                            ┌────────────────────┐
                                            │  Google Gemini     │
                                            │  (gemini-flash-latest) │
                                            └────────┬───────────┘
                                                     │
                                                     ▼
                                              Cited Answer
```

---

## 📁 Project Structure

```
RAG2/
├── .env                        # API keys (GEMINI_API_KEY)
├── docker-compose.yml          # Weaviate vector database container
├── requirements.txt            # Python dependencies
├── data/                       # Place your legal PDFs & TXT files here
├── pdfs_to_upload/             # Additional PDFs for upload via UI
│
├── app.py                      # CLI chatbot entry point
├── streamlit_app.py            # Streamlit web UI
├── ingest.py                   # Standalone ingestion runner
├── run_all.py                  # Runs ingest → CLI → Streamlit sequentially
├── run_streamlit.py            # Launches only the Streamlit app
├── test_upload.py              # Tests the document processing pipeline
├── RAG_eval.py                 # RAG evaluation with Ragas metrics
│
└── utils/                      # Core modules
    ├── config.py               # Centralised configuration & constants
    ├── database.py             # Weaviate v4 client connection
    ├── document_loader.py      # PDF/TXT loading with OCR fallback
    ├── chunking_service.py     # Legal-aware text splitting
    ├── annotation_rules.py     # Regex metadata extraction (act, section, chapter)
    ├── embedding_service.py    # HuggingFace embedding model loader
    ├── persistence_service.py  # LangChain ↔ Weaviate vector store bridge
    ├── ingestion_service.py    # End-to-end ingestion orchestrator
    ├── retrieval_service.py    # Semantic retrieval + CrossEncoder reranking
    ├── llm_service.py          # Gemini LLM initialisation & prompt template
    └── rag_service.py          # Final LangChain retrieval chain assembly
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9+ |
| Docker & Docker Compose | Latest |
| Poppler (for scanned PDF OCR) | 23.x+ |
| Tesseract OCR (optional) | 5.x+ |

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd RAG2
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root (or edit the existing one):

```env
GEMINI_API_KEY="your-google-gemini-api-key"
```

### 5. Start Weaviate

```bash
docker-compose up -d
```

This launches a local Weaviate instance on `http://localhost:8080` with gRPC on port `50051`.

### 6. Add Your Documents

Place your legal PDF or TXT files in the `data/` directory.

### 7. Run the Application

**Option A — Full pipeline (ingest + CLI + Streamlit):**

```bash
python run_all.py
```

**Option B — Ingest only:**

```bash
python ingest.py
```

**Option C — CLI chatbot only (after ingestion):**

```bash
python app.py
```

**Option D — Streamlit web UI only (after ingestion):**

```bash
python run_streamlit.py
# or directly:
streamlit run streamlit_app.py
```

The Streamlit app will be available at **http://localhost:8501**.

---

## 💬 Usage

### CLI Mode

```
🏛️  Legal RAG Chatbot
==================================================

🤔 Question: What is Section 3 of the Motor Vehicles Act?
🔍 Searching knowledge base...

📝 Answer:
----------------------------------------
Section 3 of the Motor Vehicles Act, 1988 states that...

📚 Sources:
----------------------------------------
  1. motor_vehicles_act.pdf | Act: Motor Vehicles Act, 1988 | Section 3 | Page 12
```

Type `exit`, `quit`, or `q` to close.

### Streamlit Web UI

- **Ask questions** in the chat input at the bottom of the page.
- **Upload new documents** via the sidebar — they are processed and added to the knowledge base in real time.
- **View sources** inline beneath each answer.
- Type `clear` or use the sidebar button to reset chat history.

---

## ⚙️ Configuration

All tuneable parameters live in [`utils/config.py`](utils/config.py):

| Parameter | Default | Description |
|---|---|---|
| `GEMINI_MODEL_NAME` | `gemini-flash-latest` | Google Gemini model |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Local embedding model |
| `CHUNK_SIZE` | `1500` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `INITIAL_SEMANTIC_K` | `10` | Candidates from vector search |
| `HYBRID_ALPHA` | `0.5` | 0.0 = pure BM25, 1.0 = pure vector, 0.5 = balanced |
| `FINAL_TOP_N_DOCS` | `3` | Documents after reranking |
| `RERANKER_MODEL_NAME` | `BAAI/bge-reranker-base` | CrossEncoder reranker |
| `WEAVIATE_URL` | `http://localhost:8080` | Weaviate connection URL |
| `WEAVIATE_CLASS_NAME` | `LegalDocumentChunk` | Weaviate collection name |

---

## 🧪 Testing & Evaluation

### Pipeline Test

Verify the document loading and chunking pipeline:

```bash
python test_upload.py
```

### RAG Evaluation (Ragas)

1. Generate an evaluation dataset as `rag_eval_data.json` — a JSON array of objects with keys: `question`, `generated_answer`, `ground_truth`, `contexts`.
2. Run:

```bash
python RAG_eval.py
```

Metrics reported: **Faithfulness**, **Answer Relevancy**, **Context Precision**, **Context Recall**.

---

## 🔧 OCR Setup (for Scanned PDFs)

If your legal documents are scanned images inside PDFs:

1. **Install Poppler:**
   - **Windows:** Download from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases) and extract it.
   - **macOS:** `brew install poppler`
   - **Linux:** `sudo apt-get install poppler-utils`

2. **Install Tesseract:**
   - **Windows:** Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`

3. **Set the Poppler path** (Windows only) — add to your `.env` file:

   ```env
   POPPLER_PATH=C:\path\to\poppler\Library\bin
   ```

   On macOS/Linux, Poppler is found via the system PATH automatically — no env var needed.

---

## 📦 Key Dependencies

| Package | Version | Purpose |
|---|---|---|
| `langchain` | `0.1.20` | Orchestration framework for the RAG pipeline |
| `langchain-google-genai` | `0.0.8` | Google Gemini LLM integration |
| `langchain-weaviate` | `0.0.5` | Weaviate vector store integration |
| `weaviate-client` | `4.5.3` | Weaviate v4 Python client |
| `sentence-transformers` | `5.1.0` | Local embedding model |
| `torch` | `2.8.0` | PyTorch backend for embeddings & reranker |
| `pypdf` | `5.9.0` | PDF text extraction |
| `pytesseract` / `pdf2image` | `0.3.13` / `1.17.0` | OCR for scanned PDFs |
| `streamlit` | `1.49.1` | Web UI framework |
| `ragas` | `0.0.22` | RAG evaluation metrics |

---

## 📄 License

This project is for educational and research purposes. Please ensure compliance with the licenses of all third-party models and libraries used.
