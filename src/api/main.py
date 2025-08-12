from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from datetime import datetime, timedelta

from api.models import QueryRequest, QueryResponse, SystemStatus, ErrorResponse
from core.rag_system import ComplianceRAGSystem
from core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
app_start_time = datetime.now()
rag_system = None

# Create FastAPI app
app = FastAPI(
    title="SME Compliance Assistant API",
    description="AI-powered compliance assistant for Indian SMEs using RAG technology",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    global rag_system
    
    logger.info("🚀 Starting SME Compliance Assistant API...")
    
    try:
        # Initialize RAG system
        rag_system = ComplianceRAGSystem(use_openai=False)
        
        # Load existing documents
        if not rag_system.load_documents():
            logger.warning("⚠️ No documents found in vector store. Please add documents first.")
        
        logger.info("✅ RAG system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG system: {e}")
        raise

def get_rag_system() -> ComplianceRAGSystem:
    """Dependency to get RAG system instance"""
    if rag_system is None:
        raise HTTPException(status_code=503, detail="RAG system not initialized")
    return rag_system

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with basic info"""
    return {
        "message": "SME Compliance Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=SystemStatus, tags=["Health"])
async def health_check(rag: ComplianceRAGSystem = Depends(get_rag_system)):
    """Health check endpoint"""
    try:
        stats = rag.get_system_stats()
        uptime = datetime.now() - app_start_time
        
        # Determine system status
        if stats["system_ready"]:
            status = "healthy"
        elif stats["vector_store"]["document_count"] == 0:
            status = "degraded"
        else:
            status = "healthy"
        
        return SystemStatus(
            status=status,
            document_count=stats["vector_store"]["document_count"],
            llm_type=stats["llm_type"],
            capabilities=stats["capabilities"],
            uptime=str(uptime).split('.')[0]  # Remove microseconds
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="System health check failed")

@app.post("/query", response_model=QueryResponse, tags=["Compliance"])
async def process_compliance_query(
    request: QueryRequest,
    rag: ComplianceRAGSystem = Depends(get_rag_system)
):
    """Process a compliance query and return AI-generated answer"""
    
    start_time = time.time()
    
    try:
        logger.info(f"Processing query: {request.query[:50]}...")
        
        # Process query through RAG system
        result = rag.query(request.query, k=request.max_results)
        
        # Convert to API response format
        response = QueryResponse(
            answer=result["answer"],
            confidence=result["confidence"],
            sources=[
                {
                    "source": source.get("source", "unknown"),
                    "chunk_id": source.get("chunk_id", 0),
                    "document_type": source.get("document_type", "unknown"),
                    "language": source.get("language", "en")
                }
                for source in result["sources"]
            ],
            response_time=result["response_time"]
        )
        
        logger.info(f"Query processed successfully in {result['response_time']:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )

@app.get("/stats", tags=["System"])
async def get_system_stats(rag: ComplianceRAGSystem = Depends(get_rag_system)):
    """Get detailed system statistics"""
    try:
        stats = rag.get_system_stats()
        stats["uptime"] = str(datetime.now() - app_start_time).split('.')[0]
        stats["startup_time"] = app_start_time.isoformat()
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system statistics")

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            error_type="HTTPException"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            error_type="InternalServerError"
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )