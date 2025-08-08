"""
TAIFA-FIALA Backend Startup Script
"""

import sys
from pathlib import Path

import uvicorn
from config.settings import settings

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Set environment variables if .env file exists
    env_file = backend_dir / ".env"
    if env_file.exists():
        from dotenv import load_dotenv

        load_dotenv(env_file)

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=settings.DEBUG,
    )
