# DOCMINDER/app.py

import os
from utils.database import get_weaviate_client
from utils.embedding_service import initialize_embeddings
from utils.persistence_service import get_vector_store
from utils.retrieval_service import setup_retrieval_pipeline
from utils.llm_service import initialize_llm, get_rag_prompt
from utils.rag_service import create_rag_chain
from utils.config import GEMINI_MODEL_NAME, LOCAL_DATA_PATH
from utils.ingestion_service import run_ingestion

def check_documents_and_ingest():
    """Check if documents exist and run ingestion if needed."""
    print("--- Checking for Documents and Data ---")
    
    # Check if Streamlit is already running
    try:
        response = os.system("curl -s http://localhost:8501 > nul 2>&1")
        if response == 0:
            print("⚠️ Streamlit app is already running. Please use the Streamlit interface instead.")
            print("Close this application and interact with the Streamlit app at http://localhost:8501")
            return False
    except:
        pass
    
    # Check if data directory exists
    if not os.path.exists(LOCAL_DATA_PATH):
        print(f"❌ Data directory '{LOCAL_DATA_PATH}' not found.")
        print("Please create the directory and add your legal documents (PDF/TXT files).")
        print("Then run: python ingest.py")
        return False
    
    # Check if directory has documents
    files = [f for f in os.listdir(LOCAL_DATA_PATH) 
             if f.lower().endswith(('.pdf', '.txt'))]
    
    if not files:
        print(f"❌ No documents found in '{LOCAL_DATA_PATH}'.")
        print("Please add PDF or TXT files to the data directory.")
        print("Then run: python ingest.py")
        return False
    
    print(f"✅ Found {len(files)} documents: {', '.join(files[:3])}{'...' if len(files) > 3 else ''}")
    
    # Check if Weaviate has data
    try:
        client = get_weaviate_client()
        collections = client.collections.list_all()
        collection_names = [col.name for col in collections]
        
        if "LegalDocumentChunk" in collection_names:
            collection = client.collections.get("LegalDocumentChunk")
            try:
                count = collection.aggregate.over_all(total_count=True).total_count
                if count > 0:
                    print(f"✅ Knowledge base already has {count} chunks.")
                    return True
                else:
                    print("⚠️  Knowledge base exists but is empty.")
            except:
                print("⚠️  Could not count existing chunks.")
        else:
            print("⚠️  Knowledge base not found.")
        
        # Ask user if they want to ingest
        print("\n🔄 The knowledge base needs to be populated with documents.")
        choice = input("Would you like to run the ingestion process now? (y/n): ").lower().strip()
        
        if choice in ['y', 'yes']:
            print("\n--- Running Document Ingestion ---")
            try:
                run_ingestion()
                print("✅ Document ingestion completed!")
                return True
            except Exception as e:
                print(f"❌ Error during ingestion: {e}")
                print("Please run: python ingest.py manually")
                return False
        else:
            print("Please run: python ingest.py to populate the knowledge base")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check knowledge base: {e}")
        print("Please ensure Weaviate is running and try: python ingest.py")
        return False

def main():
    """Main function to run the interactive chatbot."""
    print("🏛️  Legal RAG Chatbot")
    print("=" * 50)
    
    # Check documents and ingest if needed
    if not check_documents_and_ingest():
        print("\n❌ Cannot proceed without a populated knowledge base.")
        print("\n📋 To fix this:")
        print("1. Add PDF/TXT documents to the './data' folder")
        print("2. Run: python ingest.py")
        print("3. Then run: python app.py")
        return
    
    print(f"\n--- Initializing RAG System ---")
    print(f"🤖 Using Model: {GEMINI_MODEL_NAME}")
    
    try:
        # Initialize all components required for the RAG chain
        client = get_weaviate_client()
        embeddings = initialize_embeddings()
        vector_store = get_vector_store(client, embeddings)
        retriever = setup_retrieval_pipeline(vector_store)
        llm = initialize_llm()
        prompt = get_rag_prompt()
        rag_chain = create_rag_chain(llm, prompt, retriever)
        
        print("✅ RAG System initialized successfully!")
        
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        print("Please check your configuration and try again.")
        return
    
    print("\n--- Chatbot is Ready ---")
    print("💬 Type your legal question or 'exit' to quit.")
    print("=" * 50)

    # Interactive loop
    while True:
        question = input("\n🤔 Question: ")
        if question.lower() in ['exit', 'quit', 'q']:
            break
        if not question.strip():
            continue

        try:
            print("🔍 Searching knowledge base...")
            response = rag_chain.invoke({"input": question})
            
            print("\n📝 Answer:")
            print("-" * 40)
            print(response["answer"])

            print("\n📚 Sources:")
            print("-" * 40)
            if response.get("context"):
                for i, doc in enumerate(response["context"]):
                    source_info = doc.metadata.get('source', 'N/A')
                    act_info = doc.metadata.get('act_name', 'N/A')
                    section_info = doc.metadata.get('section_number', '')
                    
                    source_text = f"  {i+1}. {source_info}"
                    if act_info != 'N/A':
                        source_text += f" | Act: {act_info}"
                    if section_info:
                        source_text += f" | {section_info}"
                    
                    print(source_text)
            else:
                print("  ⚠️  No sources found.")

        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
            print("Please try rephrasing your question or check the system status.")
            
    print("\n👋 Chatbot Shutting Down...")
    print("Thank you for using the Legal RAG Chatbot!")

if __name__ == "__main__":
    main()