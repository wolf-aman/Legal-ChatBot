import subprocess
import sys
import os

def run_script(script_name):
    print(f"\nRunning {script_name} ...")
    result = subprocess.run([sys.executable, script_name])
    if result.returncode != 0:
        print(f"Error running {script_name}. Exiting.")
        sys.exit(result.returncode)
    print(f"{script_name} finished successfully.")

if __name__ == "__main__":
    # Run ingest.py and wait
    run_script("ingest.py")
    
    # Run app.py and wait
    run_script("app.py")
    
    # Run streamlit_app.py with Streamlit (this will block until you stop Streamlit)
    print("\nLaunching Streamlit app ...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ])