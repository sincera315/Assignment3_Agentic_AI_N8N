"""
Streamlit UI Startup Script
Launch the web interface
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

if __name__ == "__main__":
    import streamlit.web.cli as stcli
    
    print("=" * 60)
    print("🚀 Real-Time Airspace Copilot - Streamlit UI")
    print("=" * 60)
    print("📱 UI will open in your browser")
    print("🌐 Default: http://localhost:8501")
    print("=" * 60)
    print("Press CTRL+C to stop")
    print("=" * 60)
    
    sys.argv = [
        "streamlit",
        "run",
        str(project_root / "ui" / "app.py"),
        "--server.port=8501",
        "--server.address=localhost",
        "--theme.base=dark"
    ]
    
    sys.exit(stcli.main())
