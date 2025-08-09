from typing import List, Optional
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
import os
from core.config import settings

class ComplianceVectorStore:
    """Manage vector store for compliance documents"""
    
    def __init__(self, use_openai: bool = True):
        """Initialize vector store with embeddings"""
        
        # Choose embedding model based on availability
        if use_openai and settings.OPENAI_API_KEY:
            print("🔑 Using OpenAI embeddings")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=settings.OPENAI_API_KEY,
                model="text-embedding-3-small"  # Cost-effective option
            )
        else:
            print("🆓 Using free SentenceTransformer embeddings")
            self.embeddings = SentenceTransformerEmbeddings(
                model_name="all-MiniLM-L6-v2"  # Good free alternative
            )
        
        # Create vector store directory
        os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
        
        # Initialize or load existing vector store
        self.vector_store = None
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to vector store"""
        print(f"📚 Adding {len(documents)} documents to vector store...")
        
        if self.vector_store is None:
            # Create new vector store
            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.VECTOR_DB_PATH,
                collection_name="compliance_docs"
            )
        else:
            # Add to existing vector store
            self.vector_store.add_documents(documents)
        
        # Persist the data
        self.vector_store.persist()
        print("✅ Documents added and persisted")
    
    def load_existing_store(self) -> bool:
        """Load existing vector store if available"""
        try:
            self.vector_store = Chroma(
                persist_directory=settings.VECTOR_DB_PATH,
                embedding_function=self.embeddings,
                collection_name="compliance_docs"
            )
            # Test if store has data
            test_results = self.vector_store.similarity_search("test", k=1)
            print("📂 Loaded existing vector store")
            return True
        except Exception as e:
            print(f"📝 No existing vector store found: {e}")
            return False
    
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Search for similar documents"""
        if self.vector_store is None:
            print("❌ Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            print(f"🔍 Found {len(results)} relevant documents")
            return results
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def get_stats(self) -> dict:
        """Get vector store statistics"""
        if self.vector_store is None:
            return {"status": "not_initialized", "document_count": 0}
        
        try:
            # Get collection info
            collection = self.vector_store._collection
            count = collection.count()
            return {
                "status": "ready",
                "document_count": count,
                "embedding_model": type(self.embeddings).__name__
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}