import fitz  # PyMuPDF
import re
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PDF_PATH = "regulationdocs/fia_2026_f1_regulations_-_section_b_sporting_-_iss_05_-_2026-02-27.pdf"
CHROMA_DB_DIR = "./chroma_db"

def extract_and_chunk_pdf(pdf_path):
    print("Extracting text from PDF...")
    doc = fitz.open(pdf_path)
    full_text = ""
    
    # Skip the cover and index pages (usually first 2-3 pages)
    for page_num in range(3, len(doc)): 
        page = doc.load_page(page_num)
        full_text += page.get_text("text") + "\n"

    print("Chunking text by Article...")
    # Regex to find FIA Article headers (e.g., "39. SAFETY CAR" or "39 SAFETY CAR")
    # It looks for a newline, 1-2 digits, an optional dot, space, and capital letters.
    article_pattern = re.compile(r'\n(?=\d{1,2}\.?\s+[A-Z\s]+)')
    
    raw_chunks = article_pattern.split(full_text)
    
    documents = []
    for chunk in raw_chunks:
        chunk = chunk.strip()
        if len(chunk) > 50: # Filter out weird empty chunks or artifacts
            # Extract the article number/name for metadata
            first_line = chunk.split('\n')[0][:50] 
            documents.append(Document(page_content=chunk, metadata={"source": first_line}))
            
    print(f"Created {len(documents)} structured chunks.")
    return documents

def build_vector_store(documents):
    print("Loading embedding model (this runs locally on your GPU/CPU)...")
    # all-MiniLM-L6-v2 is extremely fast and great for general semantic search
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Initializing ChromaDB and embedding chunks...")
    vectorstore = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    print("Vector store built successfully! Data is saved to ./chroma_db")

if __name__ == "__main__":
    docs = extract_and_chunk_pdf(PDF_PATH)
    build_vector_store(docs)