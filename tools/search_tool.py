import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

VECTOR_STORE_DIR = "vectorstore/faiss_index"

def similarity_search(query: str, doc_type: str = None, k: int = 3):
    """Searches the local FAISS index for the top 'k' chunks matching the query string."""
    # If the index doesn't exist yet, return a warning message
    if not os.path.exists(VECTOR_STORE_DIR):
        return []
    
    # Initialize the same embedding model used during ingestion
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Load the current local vector index
    db = FAISS.load_local(VECTOR_STORE_DIR, embeddings, allow_dangerous_deserialization=True)
    
    # Apply a metadata filter if a specific document type is requested
    filter_dict = {"type": doc_type} if doc_type else None
    
    # Run the search query
    results = db.similarity_search(query, k=k, filter=filter_dict)
    return results

def search_incidents(query: str) -> str:
    """Tool: Searches specifically through historical triage tickets and logs."""
    docs = similarity_search(query, doc_type="incident", k=3)
    if not docs:
        return "No matching historical incident records found."
    
    formatted_results = "--- HISTORICAL INCIDENTS FOUND ---\n"
    for idx, doc in enumerate(docs, 1):
        formatted_results += f"\n[{idx}] Source: {doc.metadata.get('source')}\nContent: {doc.page_content}\n"
    return formatted_results

def search_rca(query: str) -> str:
    """Tool: Searches specifically through deeply analyzed Root Cause Analysis reports."""
    docs = similarity_search(query, doc_type="rca", k=2)
    if not docs:
        return "No matching historical Root Cause Analysis (RCA) documents found."
    
    formatted_results = "--- HISTORICAL RCA DOCUMENTS FOUND ---\n"
    for idx, doc in enumerate(docs, 1):
        formatted_results += f"\n[{idx}] Source: {doc.metadata.get('source')}\nContent: {doc.page_content}\n"
    return formatted_results