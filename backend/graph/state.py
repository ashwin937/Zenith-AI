"""Graph state definition for the LangGraph workflow."""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict


class ChatState(TypedDict):
    """State dictionary for the chat workflow.
    
    Attributes:
        message: The user's input message.
        history: List of previous messages in format [{"role": "user"/"assistant", "content": str}, ...].
        use_rag: Boolean flag to enable/disable RAG retrieval.
        context: List of retrieved document chunks from vector store.
        response: The AI-generated response.
        sources: List of source documents used in the response.
        sanitized: Flag indicating if input has been sanitized.
    """
    message: str
    history: List[Dict[str, str]]
    use_rag: bool
    context: List[Any]
    response: str
    sources: List[Dict[str, Any]]
    sanitized: bool
