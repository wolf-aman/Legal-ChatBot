# DOCMINDER/ingest.py

from utils.ingestion_service import run_ingestion
import warnings
import os

if __name__ == "__main__":
    # Suppress numpy warnings during ingestion
    warnings.filterwarnings("ignore", message="Numpy built with MINGW-W64 on Windows 64 bits is experimental")
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")
    
    run_ingestion()
