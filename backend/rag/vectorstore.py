"""Vector store management using ChromaDB."""

import os
import shutil
from typing import List, Optional
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from rag.embeddings import get_embeddings


def get_vectorstore() -> Chroma:
    """Get or create a ChromaDB vector store.
    
    Returns:
        Chroma: Persistent vector store for document retrieval.
    """
    chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    
    # Ensure the directory exists
    os.makedirs(chroma_dir, exist_ok=True)
    
    embeddings = get_embeddings()
    vectorstore = Chroma(
        collection_name="documents",
        embedding_function=embeddings,
        persist_directory=chroma_dir
    )
    
    return vectorstore


def add_documents(documents: List[Document]) -> None:
    """Add documents to the vector store.
    
    Args:
        documents: List of Document objects to add.
    """
    if not documents:
        return
    
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
    vectorstore.persist()


def similarity_search(query: str, k: Optional[int] = None) -> List[Document]:
    """Search for documents similar to the query.
    
    Args:
        query: The search query string.
        k: Number of results to return. Defaults to SIMILARITY_K from env.
    
    Returns:
        List of Document objects matching the query.
    """
    if k is None:
        k = int(os.getenv("SIMILARITY_K", "4"))
    
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    
    return results


def delete_document(doc_id: str) -> bool:
    """Delete a document and its vectors by source metadata.
    
    Args:
        doc_id: The document source filename to delete.
    
    Returns:
        True if document was deleted, False otherwise.
    """
    vectorstore = get_vectorstore()
    
    # Get the collection and delete documents with matching source metadata
    collection = vectorstore._collection
    
    # Query for documents with this source
    results = collection.get(
        where={"source": {"$eq": doc_id}}
    )
    
    if results['ids']:
        collection.delete(ids=results['ids'])
        vectorstore.persist()
        return True
    
    return False


def get_document_list() -> List[dict]:
    """Get list of all unique document sources in the vector store.
    
    Returns:
        List of dictionaries with document metadata.
    """
    vectorstore = get_vectorstore()
    collection = vectorstore._collection
    
    # Get all metadata
    all_data = collection.get(include=['metadatas'])
    
    # Extract unique sources
    sources = {}
    for metadata in all_data.get('metadatas', []):
        if metadata and 'source' in metadata:
            source = metadata['source']
            if source not in sources:
                sources[source] = {
                    'source': source,
                    'upload_time': metadata.get('upload_time', 'Unknown'),
                    'chunk_count': 0
                }
            sources[source]['chunk_count'] += 1
    
    return list(sources.values())


def clear_vectorstore() -> None:
    """Clear the entire vector store and delete the directory."""
    chroma_dir = os.getenv("CHROMA_DB_DIR", "./chroma_db")
    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir)
    os.makedirs(chroma_dir, exist_ok=True)