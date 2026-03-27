import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


app = FastAPI()

if load_dotenv is not None:
    load_dotenv()

print("Loading Vector Store...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
retriever = vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 5, "fetch_k": 10})


groq_api_key = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY")
groq_model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Safety guard: auto-fix legacy model value that Groq decommissioned.
if groq_model_name == "llama3-8b-8192":
    groq_model_name = "llama-3.1-8b-instant"

llm = (
    ChatGroq(
        temperature=0,
        model_name=groq_model_name,
        api_key=groq_api_key,
    )
    if groq_api_key
    else None
)


class Query(BaseModel):
    question: str


@app.post("/ask")
def ask_oracle(query: Query):
    if llm is None:
        raise HTTPException(
            status_code=500,
            detail="Missing Groq API key. Set GROQ_API_KEY (or GROK_API_KEY).",
        )

    docs = retriever.invoke(query.question)

    print("\n" + "=" * 40)
    print("--- RETRIEVED CHUNKS ---")
    for i, d in enumerate(docs):
        print(f"\nCHUNK {i + 1} (Source: {d.metadata.get('source', 'Unknown')}):")
        print(f"{d.page_content[:300]}...\n")
    print("=" * 40 + "\n")

    context = "\n\n".join(
        [f"Source: {d.metadata.get('source', 'Unknown')}\n{d.page_content}" for d in docs]
    )

    prompt = f"""
    You are the FIA Race Director's strict AI assistant. Answer the user's scenario using ONLY the provided sporting regulations.
    If the rules do not explicitly cover the scenario, state that clearly. Do not guess.
    Always cite the exact Article number you are referencing in your response.

    Official Regulations:
    {context}

    User Scenario: {query.question}
    """

    try:
        response = llm.invoke(prompt)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Groq request failed: {exc}") from exc

    return {
        "answer": response.content,
        "sources_cited": [d.metadata.get("source") for d in docs],
    }
