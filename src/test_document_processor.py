from core.document_processor import ComplianceDocumentProcessor
import os

def test_document_processing():
    """Test the document processor with sample data"""
    
    # Initialize processor
    processor = ComplianceDocumentProcessor()
    
    # Process sample file
    sample_file = "data/raw/sample_gst_info.txt"
    
    if not os.path.exists(sample_file):
        print(f"❌ Sample file not found: {sample_file}")
        print("Please create the sample file first!")
        return
    
    # Process the file
    documents = processor.process_file(sample_file)
    
    if documents:
        print(f"✅ Successfully processed {len(documents)} document chunks")
        print("\n📄 Sample chunk:")
        print(f"Content: {documents[0].page_content[:100]}...")
        print(f"Metadata: {documents[0].metadata}")
        print("\n🚀 Document processor working correctly!")
    else:
        print("❌ No documents were created")

if __name__ == "__main__":
    test_document_processing()