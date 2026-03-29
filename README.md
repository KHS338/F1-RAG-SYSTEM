# F1 RAG System (Practice Project)

This is a practice Retrieval-Augmented Generation (RAG) project built around Formula 1 sporting regulations.

The project:
- Ingests FIA regulations from PDF documents
- Chunks and embeds the text into a local Chroma vector database
- Retrieves relevant regulation chunks for a user question
- Uses Groq LLM to generate a grounded answer with cited sources
- Includes a Next.js UI in `f1-oracle-ui/`

## Project Structure

- `ingest.py`: Reads the FIA PDF, chunks by article, and builds the vector DB
- `api.py`: FastAPI backend (`/ask`) for retrieval + answer generation
- `chroma_db/`: Persisted Chroma vector store
- `regulationdocs/`: Source regulation PDF(s)
- `f1-oracle-ui/`: Next.js frontend

## Prerequisites

- Python 3.11+ (3.12 works)
- Node.js 18+ (for frontend)
- A Groq API key

## 1) Clone and open the project

```bash
git clone https://github.com/KHS338/F1-RAG-SYSTEM.git
cd F1-RAG-SYSTEM
```

## 2) Create and activate Python virtual environment

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3) Install backend dependencies

```bash
pip install fastapi uvicorn pydantic python-dotenv pymupdf \
  langchain langchain-community langchain-core langchain-huggingface \
  langchain-groq chromadb sentence-transformers
```

## 4) Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
# Optional (default is llama-3.1-8b-instant)
GROQ_MODEL=llama-3.1-8b-instant
```

## 5) Add regulation PDF

Place your FIA regulation PDF in `regulationdocs/`.

The current ingestion script expects:

`regulationdocs/fia_2026_f1_regulations_-_section_b_sporting_-_iss_05_-_2026-02-27.pdf`

If your filename is different, update `PDF_PATH` in `ingest.py`.

## 6) Build the vector store

```bash
python ingest.py
```

This creates/updates the local Chroma DB in `chroma_db/`.

## 7) Run backend API

```bash
uvicorn api:app --reload
```

Backend runs at:

`http://127.0.0.1:8000`

## 8) Test API endpoint

### cURL example

```bash
curl -X POST "http://127.0.0.1:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"When can the Safety Car be deployed?"}'
```

## 9) Run frontend (optional)

```bash
cd f1-oracle-ui
npm install
npm run dev
```

Frontend runs at:

`http://localhost:3000`

## Notes

- This repository is intended as a learning/practice RAG project.
- If you rename/move the project folder on Windows, some virtualenv launcher executables may break. If needed, run:

```bash
python -m pip install --force-reinstall uvicorn
```

- `api.py` currently allows all origins via CORS for development.

## License

No license file is currently included. Add one if you plan to distribute this project publicly.
