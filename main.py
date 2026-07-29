import os
import sys
import subprocess

def main():
    # Ensure current directory is project workspace root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)
    
    # Pre-flight database initializations
    try:
        from database.connection import init_db
        init_db()
        print("Healthcare database initialized successfully.")
    except Exception as e:
        print(f"Error initializing healthcare database: {e}")
        sys.exit(1)
        
    # Check if streamlit is installed
    try:
        import streamlit
    except ImportError:
        print("Streamlit is not installed. Please run: pip install -r requirements.txt")
        sys.exit(1)
        
    # Start streamlit server
    print("Starting Streamlit Dashboard application...")
    cmd = ["streamlit", "run", "frontend/app.py"]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nHealthcare Agent Portal terminated by user.")
    except Exception as e:
        print(f"Error starting Streamlit server: {e}")

if __name__ == "__main__":
    main()
