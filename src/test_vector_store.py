from core.document_processor import ComplianceDocumentProcessor
from core.vector_store import ComplianceVectorStore
import os

def test_vector_store():
    """Test the complete pipeline: documents -> embeddings -> search"""
    
    print("🚀 Testing Vector Store Pipeline\n")
    
    # Step 1: Process documents
    processor = ComplianceDocumentProcessor()
    sample_file = "data/raw/sample_gst_info.txt"
    
    if not os.path.exists(sample_file):
        print("❌ Sample file not found. Run Step 4 first!")
        return
    
    documents = processor.process_file(sample_file)
    print(f"📄 Processed {len(documents)} document chunks\n")
    
    # Step 2: Initialize vector store (always create fresh for testing)
    vector_store = ComplianceVectorStore(use_openai=False)
    
    # Step 3: Always add documents for testing (skip loading existing)
    print("Creating fresh vector store for testing...")
    vector_store.add_documents(documents)
    
    # Step 4: Test search functionality
    test_queries = [
        "What is the GSTR-1 due date?",
        "GST rates for restaurants",
        "Input tax credit rules",
        "Section 80C deduction limit"
    ]
    
    print("\n🔍 Testing Search Functionality:")
    print("-" * 50)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = vector_store.search(query, k=2)
        
        if results:
            for i, doc in enumerate(results):
                print(f"  Result {i+1}: {doc.page_content[:80]}...")
        else:
            print("  No results found")
    
    # Step 5: Show statistics
    stats = vector_store.get_stats()
    print(f"\n📊 Vector Store Stats:")
    print(f"   Status: {stats['status']}")
    print(f"   Documents: {stats.get('document_count', 0)}")
    print(f"   Embedding Model: {stats.get('embedding_model', 'Unknown')}")
    
    print("\n🎉 Vector store test completed!")

if __name__ == "__main__":
    test_vector_store()