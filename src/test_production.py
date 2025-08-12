from core.rag_system import ComplianceRAGSystem
from core.logger import logger
from core.performance_monitor import performance_monitor
import time

def test_production_features():
    """Test production logging and monitoring"""
    
    print("🧪 Testing Production Features")
    print("=" * 50)
    
    # Initialize RAG system
    rag = ComplianceRAGSystem(use_openai=False)
    rag.load_documents()
    
    # Test queries with monitoring
    test_queries = [
        "What is GSTR-1 due date?",
        "GST rates for restaurants",
        "Invalid query that should fail"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: {query}")
        result = rag.query(query)
        print(f"✅ Response time: {result['response_time']:.2f}s")
        print(f"📊 Confidence: {result['confidence']}")
    
    # Check performance stats
    print("\n📊 Performance Statistics:")
    stats = performance_monitor.get_current_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 Production features working!")
    print("📁 Check logs/ directory for detailed logs")

if __name__ == "__main__":
    test_production_features()