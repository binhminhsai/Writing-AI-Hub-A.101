import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Check for OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY", "")
api_key_length = len(api_key) if api_key else 0
api_key_start = api_key[:5] + "..." if api_key else "None"

# Print status of API key
if not api_key:
    logger.error("\n⚠️ WARNING: No OpenAI API key found in environment variables!")
    logger.error("Please add your API key to the .env file: OPENAI_API_KEY=your-key-here\n")
    sys.exit(1)
else:
    logger.info(f"\n✅ OpenAI API key found (starts with: {api_key_start})")

# Initialize OpenAI client
try:
    from openai import OpenAI
    logger.debug("Initializing OpenAI client...")
    openai_client = OpenAI(api_key=api_key)
    logger.debug("Client initialization successful")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

# Choose which server implementation to use
SERVER_TYPE = os.environ.get("SERVER_TYPE", "flask").lower()

if SERVER_TYPE == "flask":
    # Flask implementation (simpler, better compatibility with Replit)
    from flask import Flask, send_from_directory, redirect, request, jsonify

    app = Flask(__name__, 
                static_folder='public',
                template_folder='public')
    
    # Import routes from API app for Flask compatibility
    try:
        from app import app as fastapi_app
        logger.debug("Successfully imported FastAPI app")
    except ImportError as e:
        logger.warning(f"Could not import FastAPI app: {e}")
    except Exception as e:
        logger.error(f"Error importing FastAPI app: {e}")
    
    # Serve static files
    @app.route('/')
    def index():
        return send_from_directory('public', 'index.html')
    
    @app.route('/setting.html')
    def setting():
        return send_from_directory('public', 'setting.html')
    
    @app.route('/practice.html')
    def practice():
        return send_from_directory('public', 'practice.html')
    
    @app.route('/grading.html')
    def grading():
        return send_from_directory('public', 'grading.html')
    
    @app.route('/account.html')
    def account():
        return send_from_directory('public', 'account.html')
    
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory('public', 'favicon.ico')
    
    # Generic static file handler
    @app.route('/<path:path>')
    def static_files(path):
        # Check if the file exists in the public directory
        file_path = Path('public') / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory('public', path)
        
        # If it's not a static file, forward to FastAPI routes
        return jsonify({"error": "File not found"}), 404
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            "status": "ok",
            "openai_client": openai_client is not None,
            "api_key_present": bool(api_key)
        })
    
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 8080))
        logger.info(f"\n🚀 Starting Flask server at http://0.0.0.0:{port}")
        logger.info("Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=port, debug=True)

else:
    # FastAPI implementation (original app)
    import uvicorn
    from fastapi.staticfiles import StaticFiles
    from fastapi import FastAPI, Request
    from fastapi.responses import FileResponse
    
    try:
        from app import app
        logger.debug("Successfully imported FastAPI app")
    except ImportError as e:
        logger.warning(f"Could not import FastAPI app: {e}")
        # Create a minimal FastAPI app if the import failed
        from fastapi import FastAPI
        app = FastAPI(title="Writing AI Hub")
    
    # Root route to serve index.html
    @app.get("/")
    async def read_root():
        return FileResponse('public/index.html')
    
    # HTML page routes
    @app.get("/setting.html")
    async def get_setting():
        return FileResponse('public/setting.html')
    
    @app.get("/practice.html")
    async def get_practice():
        return FileResponse('public/practice.html')
    
    @app.get("/grading.html")
    async def get_grading():
        return FileResponse('public/grading.html')
    
    @app.get("/account.html")
    async def get_account():
        return FileResponse('public/account.html')
    
    # Favicon route
    @app.get("/favicon.ico")
    async def get_favicon():
        return FileResponse('public/favicon.ico')
    
    # Health check endpoint
    @app.get("/api/health")
    async def health_check():
        return {
            "status": "ok", 
            "openai_client": openai_client is not None,
            "api_key_present": bool(api_key)
        }
    
    # Setup static file serving
    app.mount("/css", StaticFiles(directory=Path("public/css")), name="css")
    app.mount("/js", StaticFiles(directory=Path("public/js")), name="js")
    app.mount("/img", StaticFiles(directory=Path("public/img")), name="img")
    
    if __name__ == "__main__":
        # Set default host and port
        host = "0.0.0.0"
        port = int(os.environ.get("PORT", 8080))
        
        # Run the server
        logger.info(f"\n🚀 Starting FastAPI server at http://{host}:{port}")
        logger.info("Press Ctrl+C to stop the server")
        
        try:
            uvicorn.run(
                "run_dev:app",  # Use the app from this file
                host=host,
                port=port,
                reload=True,
                workers=1
            )
        except KeyboardInterrupt:
            logger.info("\n[INFO] Server stopped")
        except Exception as e:
            logger.error(f"\n[ERROR] Error starting server: {e}")
            sys.exit(1)