"""
rag.py
---------
Builds and loads a FAISS vector store for ERP documentation.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ Missing GEMINI_API_KEY in .env")

DOCS_DIR = "data/docs"
VECTORSTORE_DIR = "data/vectorstore/faiss_index"

def build_vectorstore():
    """Build FAISS index from markdown docs."""
    loader = DirectoryLoader(DOCS_DIR, glob="*.md")
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} documents")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, chunk_overlap=100, separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️ Split into {len(chunks)} chunks")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
    vectorstore.save_local(VECTORSTORE_DIR)
    print(f"💾 FAISS index saved to {VECTORSTORE_DIR}")

def load_vectorstore():
    """Load FAISS index from disk."""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    return FAISS.load_local(
        VECTORSTORE_DIR, embeddings, allow_dangerous_deserialization=True
    )
def get_retriever():
    """Get a retriever for the vector store."""
    vectorstore = load_vectorstore()
    return vectorstore.as_retriever()

if __name__ == "__main__":
    build_vectorstore()
