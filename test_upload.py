#!/usr/bin/env python3
"""
Test script to verify document upload functionality
"""

import os
import tempfile
from utils.document_loader import load_documents
from utils.chunking_service import chunk_documents

def test_document_processing():
    """Test the document processing pipeline."""
    print("Testing document processing pipeline...")
    
    # Create a test document
    test_content = """
    Legal Document Test
    
    This is a test legal document to verify the processing pipeline.
    
    Section 1: General Provisions
    This section contains general provisions for legal matters.
    
    Section 2: Specific Rules
    This section contains specific rules and regulations.
    
    Section 3: Enforcement
    This section deals with enforcement mechanisms.
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        temp_file = f.name
    
    try:
        # Test document loading
        print(f"Created test file: {temp_file}")
        documents = load_documents(os.path.dirname(temp_file))
        print(f"Loaded {len(documents)} documents")
        
        if documents:
            # Test chunking
            chunks = chunk_documents(documents)
            print(f"Created {len(chunks)} chunks")
            
            # Display chunk information
            for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                print(f"\nChunk {i+1}:")
                print(f"Content: {chunk.page_content[:100]}...")
                print(f"Metadata: {chunk.metadata}")
            
            print("\n✅ Document processing test completed successfully!")
            return True
        else:
            print("❌ No documents were loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False
    finally:
        # Clean up
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    test_document_processing()
