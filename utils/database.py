# DOCMINDER/utils/database.py

import weaviate
from urllib.parse import urlparse
from .config import WEAVIATE_URL, WEAVIATE_CLASS_NAME

def get_weaviate_client():
    """Initializes and returns the Weaviate v4 client."""
    print(f"Connecting to Weaviate instance at {WEAVIATE_URL}...")

    # Parse the URL to extract components for the v4 client
    parsed_url = urlparse(WEAVIATE_URL)
    http_host = parsed_url.hostname
    http_port = parsed_url.port or 80
    http_secure = parsed_url.scheme == 'https'

    try:
        # Use the modern v4 client connection method
        client = weaviate.connect_to_custom(
            http_host=http_host,
            http_port=http_port,
            http_secure=http_secure,
            # Assuming gRPC is on the standard port, adjust if needed
            grpc_host=http_host,
            grpc_port=50051,
            grpc_secure=False
        )
        client.is_ready() # Check connection
        print("Successfully connected to Weaviate.")
        return client
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        print("Please ensure your Weaviate Docker container is running.")
        raise

def clear_weaviate_schema():
    """Deletes the existing class schema in Weaviate using the v4 client API."""
    client = get_weaviate_client()
    print(f"Checking for and deleting existing collection: '{WEAVIATE_CLASS_NAME}'...")
    try:
        if client.collections.exists(WEAVIATE_CLASS_NAME):
            client.collections.delete(WEAVIATE_CLASS_NAME)
            print(f"Collection '{WEAVIATE_CLASS_NAME}' deleted successfully.")
        else:
            print(f"Collection '{WEAVIATE_CLASS_NAME}' does not exist, skipping deletion.")
    except Exception as e:
        print(f"Error deleting Weaviate collection: {e}")
        raise
    finally:
        client.close() # Good practice to close the client connection

