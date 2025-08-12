import streamlit as st
import requests
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="SME Compliance Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #FF9933 0%, #FFFFFF 50%, #138808 100%);
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 2rem;
}

.stat-card {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #FF9933;
    margin: 0.5rem 0;
}

.query-result {
    background: #e8f4fd;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.confidence-high { color: #28a745; }
.confidence-medium { color: #ffc107; }
.confidence-low { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'api_status' not in st.session_state:
    st.session_state.api_status = None

def check_api_status():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def query_api(question: str, max_results: int = 3):
    """Query the compliance API"""
    try:
        payload = {
            "query": question,
            "max_results": max_results
        }
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Connection Error: {str(e)}"}

# Main header
st.markdown("""
<div class="main-header">
    <h1>🏢 SME Compliance Assistant</h1>
    <p>AI-Powered Compliance Solutions for Indian SMEs</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔧 System Status")
    
    # Check API status
    with st.spinner("Checking system status..."):
        st.session_state.api_status = check_api_status()
    
    if st.session_state.api_status:
        st.success("✅ System Online")
        
        # Display system stats
        status_data = st.session_state.api_status
        
        st.markdown(f"""
        <div class="stat-card">
            <strong>📊 System Statistics</strong><br>
            Status: {status_data['status']}<br>
            Documents: {status_data['document_count']}<br>
            LLM Type: {status_data['llm_type']}<br>
            Uptime: {status_data['uptime']}
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.error("❌ API Not Available")
        st.info("Please ensure the API server is running:\n```python src/api/main.py```")
    
    st.header("📋 Quick Examples")
    example_queries = [
        "What is the GSTR-1 due date?",
        "GST rates for restaurants",
        "Late penalty for GSTR-3B",
        "Section 80C deduction limit",
        "Input tax credit on cars",
        "GST registration documents"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{query}", use_container_width=True):
            st.session_state.current_query = query

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask Your Compliance Question")
    
    # Query input
    current_query = st.session_state.get('current_query', '')
    user_question = st.text_area(
        "Enter your compliance question:",
        value=current_query,
        height=100,
        placeholder="Example: What are the GST rates for software services?"
    )
    
    # Settings
    col_settings1, col_settings2 = st.columns(2)
    with col_settings1:
        max_results = st.slider("Max Sources", 1, 5, 3)
    with col_settings2:
        show_sources = st.checkbox("Show Source Details", True)
    
    # Query button
    if st.button("🔍 Get Answer", type="primary", use_container_width=True):
        if user_question.strip() and st.session_state.api_status:
            with st.spinner("🤖 AI is analyzing your question..."):
                
                # Query the API
                result = query_api(user_question, max_results)
                
                if "error" not in result:
                    # Display result
                    st.markdown(f"""
                    <div class="query-result">
                        <h4>📝 Answer:</h4>
                        <p>{result['answer']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Confidence indicator
                    confidence = result['confidence']
                    if confidence >= 0.8:
                        conf_class = "confidence-high"
                        conf_icon = "🟢"
                    elif confidence >= 0.6:
                        conf_class = "confidence-medium"
                        conf_icon = "🟡"
                    else:
                        conf_class = "confidence-low"
                        conf_icon = "🔴"
                    
                    st.markdown(f"""
                    <p><strong>Confidence:</strong> 
                    <span class="{conf_class}">{conf_icon} {confidence:.2%}</span> | 
                    <strong>Response Time:</strong> {result['response_time']:.2f}s</p>
                    """, unsafe_allow_html=True)
                    
                    # Source information
                    if show_sources and result['sources']:
                        st.subheader("📚 Sources Used")
                        for i, source in enumerate(result['sources'], 1):
                            with st.expander(f"Source {i}: {source['document_type']}"):
                                st.write(f"**File:** {source['source']}")
                                st.write(f"**Chunk ID:** {source['chunk_id']}")
                                st.write(f"**Language:** {source['language']}")
                    
                    # Add to history
                    st.session_state.query_history.append({
                        'timestamp': datetime.now(),
                        'question': user_question,
                        'answer': result['answer'],
                        'confidence': confidence,
                        'response_time': result['response_time']
                    })
                    
                    # Clear current query
                    if 'current_query' in st.session_state:
                        del st.session_state.current_query
                    
                else:
                    st.error(f"❌ {result['error']}")
        
        elif not user_question.strip():
            st.warning("Please enter a question!")
        else:
            st.error("API not available. Please start the server first.")

with col2:
    st.header("📊 Performance Dashboard")
    
    if st.session_state.query_history:
        # Query history
        st.subheader("🕒 Recent Queries")
        
        for i, query in enumerate(reversed(st.session_state.query_history[-5:]), 1):
            with st.expander(f"Query {i}: {query['question'][:30]}..."):
                st.write(f"**Time:** {query['timestamp'].strftime('%H:%M:%S')}")
                st.write(f"**Confidence:** {query['confidence']:.2%}")
                st.write(f"**Response Time:** {query['response_time']:.2f}s")
        
        # Performance charts
        if len(st.session_state.query_history) > 1:
            st.subheader("📈 Performance Trends")
            
            # Response time chart
            df = pd.DataFrame(st.session_state.query_history)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=df['response_time'],
                mode='lines+markers',
                name='Response Time',
                line=dict(color='#FF9933')
            ))
            fig.update_layout(
                title="Response Time Trend",
                yaxis_title="Seconds",
                height=200,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Confidence distribution
            avg_confidence = df['confidence'].mean()
            st.metric("Average Confidence", f"{avg_confidence:.2%}")
            
    else:
        st.info("No queries yet. Ask your first compliance question!")
    
    # Clear history button
    if st.session_state.query_history:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🇮🇳 Built for Indian SMEs | Powered by RAG Technology</p>
    <p>API Documentation: <a href="http://localhost:8000/docs" target="_blank">localhost:8000/docs</a></p>
</div>
""", unsafe_allow_html=True)