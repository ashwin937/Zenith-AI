"""Document loading and processing module."""

import os
from datetime import datetime
from typing import List
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    CSVLoader,
    Docx2txtLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Initialize text splitter with configured parameters.
    
    Returns:
        RecursiveCharacterTextSplitter: Configured text splitter.
    """
    chunk_size = int(os.getenv("MAX_CHUNK_SIZE", "500"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )


def load_pdf(file_path: str, filename: str) -> List[Document]:
    """Load and split a PDF file.
    
    Args:
        file_path: Path to the PDF file.
        filename: Original filename for metadata.
    
    Returns:
        List of Document objects.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    
    splitter = get_text_splitter()
    split_docs = splitter.split_documents(documents)
    
    # Add metadata
    upload_time = datetime.now().isoformat()
    for i, doc in enumerate(split_docs):
        doc.metadata['source'] = filename
        doc.metadata['upload_time'] = upload_time
        doc.metadata['chunk_index'] = i
        doc.metadata['file_type'] = 'pdf'
    
    return split_docs


def load_txt(file_path: str, filename: str) -> List[Document]:
    """Load and split a text file.
    
    Args:
        file_path: Path to the text file.
        filename: Original filename for metadata.
    
    Returns:
        List of Document objects.
    """
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    
    splitter = get_text_splitter()
    split_docs = splitter.split_documents(documents)
    
    # Add metadata
    upload_time = datetime.now().isoformat()
    for i, doc in enumerate(split_docs):
        doc.metadata['source'] = filename
        doc.metadata['upload_time'] = upload_time
        doc.metadata['chunk_index'] = i
        doc.metadata['file_type'] = 'txt'
    
    return split_docs


def load_csv(file_path: str, filename: str) -> List[Document]:
    """Load and split a CSV file.
    
    Args:
        file_path: Path to the CSV file.
        filename: Original filename for metadata.
    
    Returns:
        List of Document objects.
    """
    loader = CSVLoader(file_path, encoding='utf-8')
    documents = loader.load()
    
    splitter = get_text_splitter()
    split_docs = splitter.split_documents(documents)
    
    # Add metadata
    upload_time = datetime.now().isoformat()
    for i, doc in enumerate(split_docs):
        doc.metadata['source'] = filename
        doc.metadata['upload_time'] = upload_time
        doc.metadata['chunk_index'] = i
        doc.metadata['file_type'] = 'csv'
    
    return split_docs


def load_docx(file_path: str, filename: str) -> List[Document]:
    """Load and split a DOCX file.
    
    Args:
        file_path: Path to the DOCX file.
        filename: Original filename for metadata.
    
    Returns:
        List of Document objects.
    """
    loader = Docx2txtLoader(file_path)
    documents = loader.load()
    
    splitter = get_text_splitter()
    split_docs = splitter.split_documents(documents)
    
    # Add metadata
    upload_time = datetime.now().isoformat()
    for i, doc in enumerate(split_docs):
        doc.metadata['source'] = filename
        doc.metadata['upload_time'] = upload_time
        doc.metadata['chunk_index'] = i
        doc.metadata['file_type'] = 'docx'
    
    return split_docs


def load_and_split(file_path: str, filename: str) -> List[Document]:
    """Load and split a document based on file type.
    
    Args:
        file_path: Path to the file.
        filename: Original filename for metadata.
    
    Returns:
        List of Document objects.
    
    Raises:
        ValueError: If file type is not supported.
    """
    file_ext = Path(filename).suffix.lower()
    
    if file_ext == '.pdf':
        return load_pdf(file_path, filename)
    elif file_ext == '.txt':
        return load_txt(file_path, filename)
    elif file_ext == '.csv':
        return load_csv(file_path, filename)
    elif file_ext == '.docx':
        return load_docx(file_path, filename)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
