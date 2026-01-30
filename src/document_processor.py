"""
Document Processing Module
Handles PDF, DOCX, and TXT file parsing and chunking
"""
import io
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from docx import Document

from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_text_from_pdf(file) -> str:
    """Extract text from PDF file"""
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_text_from_docx(file) -> str:
    """Extract text from DOCX file"""
    doc = Document(file)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text


def extract_text_from_txt(file) -> str:
    """Extract text from TXT file"""
    return file.read().decode("utf-8")


def load_document(uploaded_file) -> str:
    """
    Load and extract text from uploaded file
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Extracted text as string
    """
    file_extension = uploaded_file.name.lower().split(".")[-1]
    
    # Reset file pointer
    uploaded_file.seek(0)
    
    if file_extension == "pdf":
        return extract_text_from_pdf(uploaded_file)
    elif file_extension == "docx":
        return extract_text_from_docx(uploaded_file)
    elif file_extension == "txt":
        return extract_text_from_txt(uploaded_file)
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")


def split_into_chunks(text: str, filename: str = "document") -> List[dict]:
    """
    Split text into chunks for embedding
    
    Args:
        text: Full document text
        filename: Name of the source file
        
    Returns:
        List of document chunks with metadata
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    
    # Add metadata to each chunk
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append({
            "content": chunk,
            "metadata": {
                "source": filename,
                "chunk_id": i
            }
        })
    
    return documents


def process_document(uploaded_file) -> List[dict]:
    """
    Full document processing pipeline
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        List of document chunks ready for embedding
    """
    # Extract text
    text = load_document(uploaded_file)
    
    if not text.strip():
        raise ValueError("Document appears to be empty or could not be read")
    
    # Split into chunks
    chunks = split_into_chunks(text, uploaded_file.name)
    
    return chunks
