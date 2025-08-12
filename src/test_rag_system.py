from core.rag_system import ComplianceRAGSystem
from core.document_processor import ComplianceDocumentProcessor
import os
import json

def test_complete_rag_system():
    """Test the complete RAG pipeline"""
    
    print("🚀 Testing Complete RAG System\n")
    print("=" * 60)
    
    # Initialize RAG system
    rag_system = ComplianceRAGSystem(use_openai=False)  # Use free/local LLM
    
    # Load documents if available
    if not rag_system.load_documents():
        print("📚 No existing documents found. Loading sample data...")

        # Process and add documents
        processor = ComplianceDocumentProcessor()
        sample_file = "data/raw/sample_gst_info.txt"
        
        if os.path.exists(sample_file):
            documents = processor.process_file(sample_file)
            rag_system.vector_store.add_documents(documents)
            print("✅ Documents loaded successfully\n")
        else:
            print("❌ Sample file not found. Please run previous steps first!")
            return
    
    # Test queries
    test_queries = [
        "What is the due date for GSTR-1 filing?",
        "What are the GST rates for restaurants?", 
        "How much penalty for late GSTR-3B filing?",
        "What is the maximum Section 80C deduction?",
        "Can I claim input tax credit on motor cars?",
        "What documents are needed for GST registration?"  # This should show lower confidence
    ]
    
    print("🔍 Testing RAG Queries:")
    print("-" * 60)
    
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        
        result = rag_system.query(query)
        results.append({"query": query, **result})
        
        print(f"📝 Answer: {result['answer'][:150]}...")
        print(f"🎯 Confidence: {result['confidence']}")
        print(f"⏱️  Response Time: {result['response_time']:.2f}s")
        print(f"📚 Sources Used: {len(result['sources'])}")
        
        if result['sources']:
            print("📖 Source Details:")
            for j, source in enumerate(result['sources']):
                print(f"   Source {j+1}: {source.get('source', 'Unknown')}")
    
    # System statistics
    print(f"\n{'='*60}")
    print("📊 System Statistics:")
    stats = rag_system.get_system_stats()
    print(json.dumps(stats, indent=2))
    
    # Performance summary
    avg_response_time = sum(r['response_time'] for r in results) / len(results)
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    
    print(f"\n🎯 Performance Summary:")
    print(f"   Average Response Time: {avg_response_time:.2f}s")
    print(f"   Average Confidence: {avg_confidence:.2f}")
    print(f"   Queries Processed: {len(results)}")
    
    print(f"\n🎉 RAG System Test Completed!")
    print("Your AI compliance assistant is working! 🤖")

if __name__ == "__main__":
    test_complete_rag_system()