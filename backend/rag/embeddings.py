"""Embeddings module using Ollama's nomic-embed-text model."""

import os
from langchain_ollama import OllamaEmbeddings


def get_embeddings():
    """Initialize and return Ollama embeddings model.
    
    Returns:
        OllamaEmbeddings: Configured embeddings model using nomic-embed-text.
    """
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    
    embeddings = OllamaEmbeddings(
        base_url=ollama_base_url,
        model=embed_model
    )
    return embeddings
