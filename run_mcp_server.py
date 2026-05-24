"""
MCP Server Startup Script
Launch the FastAPI MCP server
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

# Import and run server
if __name__ == "__main__":
    import uvicorn
    from mcp_server.main import app
    
    host = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_SERVER_PORT", "8000"))
    
    print("=" * 60)
    print("🚀 Real-Time Airspace Copilot - MCP Server")
    print("=" * 60)
    print(f"📡 Server: http://{host}:{port}")
    print(f"❤️  Health: http://{host}:{port}/health")
    print(f"🔧 Tools: http://{host}:{port}/mcp/tools")
    print("=" * 60)
    print("Press CTRL+C to stop")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
