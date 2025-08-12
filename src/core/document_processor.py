from typing import List
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

class ComplianceDocumentProcessor:
    """Process compliance documents for RAG system"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # Small chunks for better retrieval
            chunk_overlap=50,  # Some overlap to maintain context
            separators=["\n\n", "\n", ".", " "]  # Split on these characters
        )
    
    def load_text_file(self, file_path: str) -> str:
        """Load text from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error loading file {file_path}: {e}")
            return ""
    
    def create_documents(self, text: str, source: str) -> List[Document]:
        """Convert text into Document objects with metadata"""
        chunks = self.text_splitter.split_text(text)
        
        documents = [] 
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "chunk_id": i,
                    "document_type": "compliance_guide",
                    "language": "en"
                }
            )
            documents.append(doc)
    
        return documents
    
    def process_file(self, file_path: str) -> List[Document]:
        """Complete processing pipeline for a single file"""
        print(f"Processing file: {file_path}")
        
        # Load text
        text = self.load_text_file(file_path)
        if not text:
            return []
        
        # Create documents
        documents = self.create_documents(text, file_path)
        
        print(f"Created {len(documents)} document chunks")
        return documents