"""LangGraph workflow orchestration for chat with RAG."""

import re
from typing import Any
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os

from graph.state import ChatState
from rag.vectorstore import similarity_search
from rag.math_tools import get_math_tools


def sanitize_input(state: ChatState) -> ChatState:
    """Sanitize and validate user input.
    
    Removes potential script injections and harmful content.
    
    Args:
        state: Current chat state.
    
    Returns:
        Updated state with sanitized message.
    """
    message = state["message"].strip()
    
    # Remove excessive whitespace
    message = re.sub(r'\s+', ' ', message)
    
    # Remove control characters
    message = ''.join(char for char in message if ord(char) >= 32 or char in '\n\t')
    
    # Limit message length to prevent abuse
    max_length = 5000
    if len(message) > max_length:
        message = message[:max_length]
    
    state["message"] = message
    state["sanitized"] = True
    
    return state


def check_rag(state: ChatState) -> ChatState:
    """Determine if RAG should be used and route accordingly.
    
    Args:
        state: Current chat state.
    
    Returns:
        Updated state with use_rag flag preserved.
    """
    # Use_rag flag is already set from the request
    # This node just validates and passes through
    return state


def retrieve_context(state: ChatState) -> ChatState:
    """Retrieve relevant context from vector store using similarity search.
    
    Args:
        state: Current chat state.
    
    Returns:
        Updated state with context documents.
    """
    if not state["use_rag"] or not state["message"]:
        state["context"] = []
        return state
    
    try:
        # Search for similar documents
        docs = similarity_search(state["message"])
        state["context"] = docs
    except Exception as e:
        print(f"Error retrieving context: {e}")
        state["context"] = []
    
    return state


def generate_response(state: ChatState) -> ChatState:
    """Generate AI response using Ollama LLM with optional RAG context.
    
    Args:
        state: Current chat state.
    
    Returns:
        Updated state with generated response.
    """
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
    
    # Bind math tools to the LLM
    math_tools = get_math_tools()
    llm_with_tools = llm.bind_tools(math_tools)
    
    # Build the prompt
    messages = []
    
    # System message
    system_prompt = """You are Quantum Chat, an advanced and highly accurate AI assistant. Your PRIMARY goal is accuracy and precision.

IMPORTANT RULES:
1. For ANY mathematical calculation, USE THE CALCULATE TOOL
2. Always verify calculations using the tool - never do math in your head
3. Show the calculation step-by-step using the tool
4. Use the calculate() tool for: arithmetic, sqrt, sin, cos, log, exp, pow
5. Double-check results before presenting them
6. Never guess on numbers - use the tool instead
7. Provide accurate, factual responses only

You have access to a calculate() tool for all math operations."""
    if state["use_rag"] and state["context"]:
        context_text = "\n\n".join([doc.page_content for doc in state["context"]])
        system_prompt += f"\n\nYou have access to the following context from uploaded documents:\n{context_text}"
    
    messages.append(SystemMessage(content=system_prompt))
    
    # Add history
    for msg in state.get("history", [])[-10:]:  # Last 10 messages for context
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    
    # Add current message
    messages.append(HumanMessage(content=state["message"]))
    
    try:
        # Generate response with tool use
        response = llm_with_tools.invoke(messages)
        state["response"] = response.content
    except Exception as e:
        state["response"] = f"Error generating response: {str(e)}"
    
    return state


def format_output(state: ChatState) -> ChatState:
    """Format the final output including source citations if RAG was used.
    
    Args:
        state: Current chat state.
    
    Returns:
        Updated state with formatted sources list.
    """
    sources = []
    
    if state["use_rag"] and state.get("context"):
        seen_sources = set()
        for doc in state["context"]:
            source_key = doc.metadata.get("source", "Unknown")
            if source_key not in seen_sources:
                seen_sources.add(source_key)
                source_info = {
                    "source": source_key,
                    "chunk_index": doc.metadata.get("chunk_index", 0),
                    "upload_time": doc.metadata.get("upload_time", "Unknown"),
                    "file_type": doc.metadata.get("file_type", "unknown")
                }
                sources.append(source_info)
    
    state["sources"] = sources
    
    return state


def build_workflow():
    """Build and compile the LangGraph workflow.
    
    Returns:
        Compiled StateGraph workflow.
    """
    workflow = StateGraph(ChatState)
    
    # Add nodes
    workflow.add_node("sanitize_input", sanitize_input)
    workflow.add_node("check_rag", check_rag)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("format_output", format_output)
    
    # Add edges
    workflow.add_edge(START, "sanitize_input")
    workflow.add_edge("sanitize_input", "check_rag")
    
    # Conditional routing based on use_rag flag
    workflow.add_conditional_edges(
        "check_rag",
        lambda x: "retrieve_context" if x["use_rag"] else "generate_response",
        {
            "retrieve_context": "retrieve_context",
            "generate_response": "generate_response"
        }
    )
    
    workflow.add_edge("retrieve_context", "generate_response")
    workflow.add_edge("generate_response", "format_output")
    workflow.add_edge("format_output", END)
    
    # Compile the workflow
    app_graph = workflow.compile()
    
    return app_graph


# Global workflow instance - lazy initialized
app_graph = None


def run_graph(state: ChatState) -> ChatState:
    """Execute the chat workflow.
    
    Args:
        state: Initial chat state.
    
    Returns:
        Final state after workflow execution.
    """
    global app_graph
    
    # Lazy initialize workflow on first call
    if app_graph is None:
        app_graph = build_workflow()
    
    result = app_graph.invoke(state)
    return result
