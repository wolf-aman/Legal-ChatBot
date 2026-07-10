# DOCMINDER/streamlit_app.py

import streamlit as st
import time
import os
import tempfile
from utils.database import get_weaviate_client
from utils.embedding_service import initialize_embeddings
from utils.persistence_service import get_vector_store
from utils.retrieval_service import setup_retrieval_pipeline
from utils.llm_service import initialize_llm, get_rag_prompt
from utils.rag_service import create_rag_chain
from utils.config import GEMINI_MODEL_NAME
from utils.document_loader import load_documents
from utils.chunking_service import chunk_documents

# Configure Streamlit page
st.set_page_config(
    page_title="Legal RAG Chatbot",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #1f77b4;
    }
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #28a745;
    }
    .source-item {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.25rem 0;
        border-left: 3px solid #6c757d;
    }
    .model-info {
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.25rem;
        border-left: 3px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_rag_system():
    """Initialize the RAG system components with caching."""
    try:
        with st.spinner("Initializing Legal RAG Chatbot..."):
            # Initialize all components required for the RAG chain
            client = get_weaviate_client()
            embeddings = initialize_embeddings()
            vector_store = get_vector_store(client, embeddings)
            retriever = setup_retrieval_pipeline(vector_store)
            llm = initialize_llm()
            prompt = get_rag_prompt()
            rag_chain = create_rag_chain(llm, prompt, retriever)
            
        return rag_chain
    except Exception as e:
        st.error(f"Failed to initialize RAG system: {str(e)}")
        return None

def process_uploaded_documents(uploaded_files):
    """Process uploaded documents and add them to the knowledge base."""
    if not uploaded_files:
        return False, "No files uploaded"
    
    try:
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp()
        temp_files = []
        
        # Save uploaded files to temporary directory
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            temp_files.append(file_path)
        
        # Load documents from temporary files
        documents = []
        for file_path in temp_files:
            try:
                if file_path.lower().endswith('.pdf'):
                    from langchain_community.document_loaders import PyPDFLoader
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                elif file_path.lower().endswith('.txt'):
                    from langchain_community.document_loaders import TextLoader
                    loader = TextLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
            except Exception as e:
                st.warning(f"Failed to load {os.path.basename(file_path)}: {str(e)}")
                continue
        
        if not documents:
            return False, "No valid documents could be processed"
        
        # Chunk the documents
        chunks = chunk_documents(documents)
        if not chunks:
            return False, "No chunks were created from the documents"
        
        # Get vector store and add documents
        client = get_weaviate_client()
        embeddings = initialize_embeddings()
        vector_store = get_vector_store(client, embeddings)
        
        # Add documents to vector store
        vector_store.add_documents(chunks)
        
        # Clean up temporary files
        for file_path in temp_files:
            try:
                os.remove(file_path)
            except:
                pass
        os.rmdir(temp_dir)
        
        return True, f"Successfully processed {len(documents)} documents and {len(chunks)} chunks"
        
    except Exception as e:
        return False, f"Error processing documents: {str(e)}"

def display_sources(sources):
    """Display source documents in a formatted way."""
    if not sources:
        st.info("No sources found.")
        return
    
    st.markdown("**📚 Sources:**")
    for i, doc in enumerate(sources, 1):
        source_info = doc.metadata.get('source', 'N/A')
        act_info = doc.metadata.get('act_name', 'N/A')
        section_info = doc.metadata.get('section_number', '')
        chapter_info = doc.metadata.get('chapter_name', '')
        
        # Create a more detailed source display
        source_text = f"**{i}.** {source_info}"
        if act_info != 'N/A':
            source_text += f" (Act: {act_info})"
        if section_info:
            source_text += f" - Section: {section_info}"
        if chapter_info:
            source_text += f" - Chapter: {chapter_info}"
        
        st.markdown(f'<div class="source-item">{source_text}</div>', unsafe_allow_html=True)

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<div class="main-header">⚖️ Legal RAG Chatbot</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        st.markdown(f'<div class="model-info">**Model:** {GEMINI_MODEL_NAME}</div>', unsafe_allow_html=True)
        
        st.header("📊 System Status")
        if 'rag_chain' in st.session_state and st.session_state.rag_chain:
            st.success("✅ RAG System Ready")
        else:
            st.error("❌ RAG System Not Initialized")
        
        st.header("📤 Document Upload")
        st.markdown("Upload legal documents to add them to the knowledge base:")
        
        # File upload widget
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'txt'],
            accept_multiple_files=True,
            help="Upload PDF or TXT files to add to the knowledge base"
        )
        
        # Show uploaded files info
        if uploaded_files:
            st.markdown("**📁 Selected Files:**")
            for file in uploaded_files:
                file_size = len(file.getvalue()) / 1024  # Size in KB
                st.markdown(f"• {file.name} ({file_size:.1f} KB)")
        
        # Process uploaded files
        if uploaded_files:
            if st.button("🚀 Process Documents", type="primary"):
                with st.spinner("Processing documents..."):
                    success, message = process_uploaded_documents(uploaded_files)
                    if success:
                        st.success(message)
                        # Clear the RAG system cache to refresh with new documents
                        if 'rag_chain' in st.session_state:
                            del st.session_state.rag_chain
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        st.header("💡 Tips")
        st.markdown("""
        - Ask specific legal questions
        - Upload documents to expand knowledge base
        - Sources are provided for transparency
        - Type 'clear' to reset chat history
        """)
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History", type="secondary"):
            st.session_state.messages = []
            st.rerun()
    
    # Initialize RAG system
    if 'rag_chain' not in st.session_state:
        st.session_state.rag_chain = initialize_rag_system()
    
    if st.session_state.rag_chain is None:
        st.error("❌ Failed to initialize the RAG system. Please check your configuration and try again.")
        st.stop()
    
    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                
                # Display sources if available
                if "sources" in message and message["sources"]:
                    display_sources(message["sources"])
    
    # Chat input
    st.markdown("---")
    
    # Create two columns for input and button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask a legal question:",
            placeholder="Enter your legal question here...",
            key="user_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("Send", type="primary", use_container_width=True)
    
    # Process user input
    if send_button and user_input:
        # Handle special commands
        if user_input.lower() in ['clear', 'reset']:
            st.session_state.messages = []
            st.rerun()
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            try:
                response = st.session_state.rag_chain.invoke({"input": user_input})
                
                # Add assistant response to chat history
                assistant_message = {
                    "role": "assistant", 
                    "content": response["answer"],
                    "sources": response.get("context", [])
                }
                st.session_state.messages.append(assistant_message)
                
                # Rerun to display the new message
                st.rerun()
                
            except Exception as e:
                error_message = f"An error occurred: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": error_message,
                    "sources": []
                })
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #6c757d; font-size: 0.8rem;'>
            Legal RAG Chatbot | Powered by Gemini & Weaviate
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
