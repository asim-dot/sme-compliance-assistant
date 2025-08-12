from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class QueryRequest(BaseModel):
    """Request model for compliance queries"""
    query: str = Field(..., description="The compliance question to ask", min_length=5, max_length=500)
    max_results: int = Field(default=3, description="Maximum number of source documents to retrieve", ge=1, le=10)
    
    class Config:
        schema_extra = {
            "example": {
                "query": "What is the due date for GSTR-1 filing?",
                "max_results": 3
            }
        }

class SourceInfo(BaseModel):
    """Information about a source document"""
    source: str
    chunk_id: int
    document_type: str
    language: str

class QueryResponse(BaseModel):
    """Response model for compliance queries"""
    answer: str = Field(..., description="AI-generated answer to the query")
    confidence: float = Field(..., description="Confidence score between 0 and 1", ge=0, le=1)
    sources: List[SourceInfo] = Field(..., description="Source documents used for the answer")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the query was processed")
    
    class Config:
        schema_extra = {
            "example": {
                "answer": "GSTR-1 filing is due on the 11th of every month for the previous month's transactions.",
                "confidence": 0.95,
                "sources": [
                    {
                        "source": "data/raw/sample_gst_info.txt",
                        "chunk_id": 1,
                        "document_type": "compliance_guide",
                        "language": "en"
                    }
                ],
                "response_time": 2.34,
                "timestamp": "2024-01-15T10:30:00"
            }
        }

class SystemStatus(BaseModel):
    """System health and status"""
    status: str = Field(..., description="System status: 'healthy', 'degraded', or 'down'")
    document_count: int = Field(..., description="Number of documents in vector store")
    llm_type: str = Field(..., description="Type of LLM being used")
    capabilities: List[str] = Field(..., description="Available system capabilities")
    uptime: str = Field(..., description="System uptime")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    error_type: str = Field(..., description="Type of error")
    timestamp: datetime = Field(default_factory=datetime.now)