"""
vector_service.py
-----------------
Handles the RAG system for projects. Indexes documents (SRS, DRD, Reports) 
into ChromaDB and provides query capabilities.
"""

import os
import logging
from typing import List, Dict, Any
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from agent import config

logger = logging.getLogger(__name__)

# Use a local, lightweight embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

VECTOR_DB_DIR = config.BASE_DIR / "data" / "vector_dbs"
os.makedirs(VECTOR_DB_DIR, exist_ok=True)

def index_project_data(project_id: str, doc_map: Dict[str, str]):
    """
    Indexes project documents into a dedicated project vector store.
    doc_map: {"srs": content, "drd": content, "report": content}
    """
    project_db_path = str(VECTOR_DB_DIR / project_id)
    
    docs = []
    for doc_type, content in doc_map.items():
        if content:
            docs.append(Document(
                page_content=content,
                metadata={"project_id": project_id, "type": doc_type}
            ))
    
    if not docs:
        logger.warning(f"No documents to index for project {project_id}")
        return

    logger.info(f"Indexing {len(docs)} documents for project {project_id} at {project_db_path}")
    
    # Initialize/overwrite vector store for this project
    vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=project_db_path,
        collection_name=f"project_{project_id}"
    )
    # Chroma persists automatically on creation from_documents in newer versions
    # but we can call it explicitly if needed in older ones.
    logger.info(f"Successfully indexed project {project_id}")

def query_project_data(project_id: str, query: str) -> str:
    """
    Queries the project-specific RAG system.
    """
    project_db_path = str(VECTOR_DB_DIR / project_id)
    
    if not os.path.exists(project_db_path):
        return f"No documentation found for project {project_id}. Please initiate the agent first."

    vector_store = Chroma(
        persist_directory=project_db_path,
        embedding_function=embedding_model,
        collection_name=f"project_{project_id}"
    )
    
    # Retrieve relevant contexts
    results = vector_store.similarity_search(query, k=1)
    context = "\n\n".join([r.page_content for r in results])
    
    # Drastic truncation for strict TPM limits
    if len(context) > 3000:
        context = context[:3000] + "..."
    
    # Use a more efficient/standard model for the chat to avoid rate limits
    rag_model = "llama-3.1-8b-instant" 
    
    from langchain_groq import ChatGroq
    llm = ChatGroq(
        model=rag_model,
        temperature=0.1,
        groq_api_key=config.GROQ_API_KEY,
    )
    
    from langchain_core.messages import HumanMessage
    
    prompt = f"""Use the context to answer. Be concise.
Context: {context}
Question: {query}"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        with open("rag_error.txt", "a") as f:
            import traceback
            f.write(f"\n--- Error at {project_id} ---\n{str(e)}\n{traceback.format_exc()}\n")
        logger.error(f"Error querying RAG LLM: {e}", exc_info=True)
        return f"Sorry, I encountered an error: {str(e)}"
