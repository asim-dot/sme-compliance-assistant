from typing import List, Dict, Optional
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_community.llms.ollama import Ollama
from langchain.chains import LLMChain
from core.logger import logger
from core.performance_monitor import performance_monitor
import time

from core.vector_store import ComplianceVectorStore
from core.config import settings

class ComplianceRAGSystem:
    """Complete RAG system for compliance queries"""
    
    def __init__(self, use_openai: bool = True):
        """Initialize RAG system with LLM and vector store"""
        
        # Initialize vector store
        self.vector_store = ComplianceVectorStore(use_openai=False)  # Keep using free embeddings
        
        # Initialize LLM
        if use_openai and settings.OPENAI_API_KEY:
            print("🔑 Using OpenAI LLM")
            self.llm = OpenAI(
                openai_api_key=settings.OPENAI_API_KEY,
                temperature=0.1,  # Low temperature for factual responses
                max_tokens=500
            )
            self.llm_type = "openai"
        else:
            print("🆓 Using Ollama (local LLM)")
            print("Note: Make sure Ollama is installed with a model like 'llama2' or 'mistral'")
            try:
                self.llm = Ollama(model="mistral:7b", temperature=0.1)
                self.llm_type = "ollama"
            except Exception as e:
                print(f"❌ Ollama not available: {e}")
                print("Using mock LLM for testing")
                self.llm = None
                self.llm_type = "mock"
        
        # Create specialized prompt for Indian compliance
        self.prompt = self._create_compliance_prompt()
        
        # Initialize chain
        if self.llm:
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
    
    def _create_compliance_prompt(self) -> PromptTemplate:
        """Create specialized prompt for Indian compliance queries"""
        template = """You are an expert Indian tax and compliance consultant specializing in GST, Income Tax, and business regulations for SMEs (Small and Medium Enterprises).

Context Information:
{context}

User Question: {question}

Instructions:
1. Provide accurate, actionable advice based on the context
2. Always cite specific sections, rules, or dates when available
3. If discussing deadlines, mention the exact due dates
4. If mentioning penalties, specify the amounts
5. Keep responses concise but complete
6. If the context doesn't contain enough information, say so clearly
7. Focus on practical implications for SME business owners

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _mock_llm_response(self, context: str, question: str) -> str:
        """Mock LLM response for testing when no LLM is available"""
        return f"""Based on the provided context, here's what I found regarding your question about "{question}":

{context[:200]}...

Please note: This is a mock response. For production use, please configure OpenAI API key or install Ollama with a language model.

Key points from the context:
- Information is available in the compliance documents
- For detailed advice, please consult with a qualified CA
- Always verify current rates and deadlines with official sources"""
    
    def load_documents(self) -> bool:
        """Load existing vector store or indicate documents need to be added"""
        return self.vector_store.load_existing_store()
    
    def query(self, question: str, k: int = 3) -> Dict:
        """Process a compliance query using RAG with monitoring"""
    
    # Start monitoring
        start_time = performance_monitor.start_query()
        
        try:
            logger.log_system_event("query_started", {"query_length": len(question)})
            
            print(f"🔍 Processing query: {question}")
            
            # Step 1: Retrieve relevant documents
            relevant_docs = self.vector_store.search(question, k=k)
            
            if not relevant_docs:
                result = {
                    "answer": "I couldn't find relevant information in the compliance documents. Please try rephrasing your question or consult with a qualified CA.",
                    "sources": [],
                    "confidence": 0.0,
                    "response_time": time.time() - start_time
                }
                
                # Log unsuccessful query
                performance_monitor.end_query(start_time, success=False)
                logger.log_query(question, result["response_time"], 0.0, 0, success=False)
                
                return result
            
            # Step 2: Prepare context
            context = self._prepare_context(relevant_docs)
            
            # Step 3: Generate response
            if self.llm_type == "mock":
                answer = self._mock_llm_response(context, question)
            else:
                try:
                    response = self.chain.run(context=context, question=question)
                    answer = response.strip()
                except Exception as e:
                    print(f"❌ LLM error: {e}")
                    logger.log_error(e, "LLM processing")
                    answer = self._mock_llm_response(context, question)
            
            # Step 4: Calculate confidence
            confidence = self._calculate_confidence(relevant_docs, question)
            
            response_time = time.time() - start_time
            
            result = {
                "answer": answer,
                "sources": [doc.metadata for doc in relevant_docs],
                "confidence": confidence,
                "response_time": response_time,
                "context_used": context[:200] + "..." if len(context) > 200 else context
            }
            
            # Log successful query
            performance_monitor.end_query(start_time, success=True)
            logger.log_query(question, response_time, confidence, len(relevant_docs), success=True)
            
            return result
            
        except Exception as e:
            # Handle any unexpected errors
            response_time = time.time() - start_time
            performance_monitor.end_query(start_time, success=False)
            logger.log_error(e, f"Query processing failed: {question[:50]}")
            
            return {
                "answer": "I encountered an error processing your question. Please try again or contact support.",
                "sources": [],
                "confidence": 0.0,
                "response_time": response_time
            }
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents):
            context_parts.append(f"Source {i+1}: {doc.page_content}")
        
        return "\n\n".join(context_parts)
    
    def _calculate_confidence(self, documents: List[Document], question: str) -> float:
        """Calculate confidence score based on document relevance"""
        if not documents:
            return 0.0
        
        # Simple confidence calculation based on:
        # 1. Number of documents found
        # 2. Length of documents (longer = more detailed)
        # 3. Keyword overlap
        
        base_confidence = min(len(documents) / 3.0, 1.0)  # More docs = higher confidence
        
        # Check for specific compliance keywords in results
        compliance_keywords = ["gst", "tax", "return", "filing", "deadline", "penalty", "rate"]
        question_lower = question.lower()
        
        keyword_bonus = 0
        for doc in documents:
            doc_lower = doc.page_content.lower()
            for keyword in compliance_keywords:
                if keyword in question_lower and keyword in doc_lower:
                    keyword_bonus += 0.1
        
        confidence = min(base_confidence + keyword_bonus, 1.0)
        return round(confidence, 2)
    
    def get_system_stats(self) -> Dict:
        """Get system statistics"""
        vector_stats = self.vector_store.get_stats()
        
        return {
            "vector_store": vector_stats,
            "llm_type": self.llm_type,
            "system_ready": vector_stats.get("document_count", 0) > 0,
            "capabilities": [
                "Document retrieval",
                "Semantic search", 
                "AI-powered responses",
                "Confidence scoring",
                "Source attribution"
            ]
        }