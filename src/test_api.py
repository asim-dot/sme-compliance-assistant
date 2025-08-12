import requests
import json
import time

def test_api_endpoints():
    """Test all API endpoints"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🧪 Testing SME Compliance Assistant API")
    print("=" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Health endpoint working")
            print(f"   Status: {health['status']}")
            print(f"   Documents: {health['document_count']}")
            print(f"   LLM Type: {health['llm_type']}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    # Test 3: Query endpoint
    print("\n3. Testing query endpoint...")
    test_queries = [
        "What is the GSTR-1 due date?",
        "GST rates for restaurants",
        "Section 80C deduction limit"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   3.{i} Query: {query}")
        try:
            payload = {
                "query": query,
                "max_results": 3
            }
            
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/query",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            api_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success (API time: {api_time:.2f}s)")
                print(f"   📝 Answer: {result['answer'][:100]}...")
                print(f"   🎯 Confidence: {result['confidence']}")
                print(f"   📚 Sources: {len(result['sources'])}")
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    # Test 4: Stats endpoint
    print("\n4. Testing stats endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Stats endpoint working")
            print(f"   System Ready: {stats['system_ready']}")
            print(f"   Uptime: {stats['uptime']}")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats endpoint error: {e}")
    
    print(f"\n🎉 API testing completed!")
    print(f"📖 API Documentation: {BASE_URL}/docs")

if __name__ == "__main__":
    test_api_endpoints()