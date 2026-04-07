"""LangChain RAG chain for question answering."""

import os
from typing import Dict, List, Any
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from rag.vectorstore import get_vectorstore


def get_rag_chain():
    """Initialize and return the RAG chain.
    
    Returns:
        RetrievalQA: Configured retrieval QA chain with Ollama LLM.
    """
    # Initialize the LLM
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model_name = os.getenv("OLLAMA_MODEL", "llama2")
    
    llm = ChatOllama(
        base_url=ollama_base_url,
        model=model_name,
        temperature=0.3,
        num_predict=256,
        top_k=40,
        top_p=0.9,
        # Mistral-specific optimizations for sliding window attention
        num_ctx=2048,  # Context window for sliding window attention
        num_batch=512,  # Batch size for faster processing
        num_thread=8,  # Use more threads for parallel processing
        repeat_penalty=1.0,  # Standard penalty
        mirostat=0  # Disable mirostat (faster)
    )
    
    # Create prompt template
    prompt_template = """You are Quantum Chat, an advanced and highly accurate AI assistant. Your PRIMARY goal is accuracy and precision.

IMPORTANT RULES FOR CALCULATIONS:
1. For ANY mathematical calculation, show your work step-by-step
2. Double-check all arithmetic
3. Be explicit about each calculation step
4. If unsure about any calculation, state your uncertainty clearly
5. Never guess on numbers - verify each step

Use the following context to answer the question with maximum accuracy:

Context:
{context}

Question: {question}

Answer: (Show step-by-step reasoning for any calculations)"""
    
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )
    
    # Get vector store
    vectorstore = get_vectorstore()
    
    # Create RetrievalQA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": int(os.getenv("SIMILARITY_K", "4"))}
        ),
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return chain


def run_rag_query(query: str, history: List[Dict[str, str]] = None) -> Dict[str, Any]:
    """Run a RAG query and return answer with sources.
    
    Args:
        query: The user query string.
        history: Conversation history (not used in basic RAG but useful for context).
    
    Returns:
        Dictionary with 'answer' and 'sources' keys.
    """
    if history is None:
        history = []
    
    chain = get_rag_chain()
    result = chain({"query": query})
    
    # Extract source information
    sources = []
    if "source_documents" in result:
        for doc in result["source_documents"]:
            source_info = {
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_index": doc.metadata.get("chunk_index", 0),
                "upload_time": doc.metadata.get("upload_time", "Unknown"),
                "content_preview": doc.page_content[:200] + "..."
            }
            sources.append(source_info)
    
    return {
        "answer": result["result"],
        "sources": sources
    }
