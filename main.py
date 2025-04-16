import os
import sys
import logging
from flask import Flask, send_from_directory, request, jsonify
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for OpenAI API key
api_key = os.environ.get("OPENAI_API_KEY", "")
api_key_length = len(api_key) if api_key else 0
api_key_start = api_key[:10] + "..." if api_key else "None"

logger.debug(f"API key present: {bool(api_key)}, length: {api_key_length}")
logger.debug(f"API key starts with: {api_key_start}")

try:
    from openai import OpenAI
    logger.debug("Initializing OpenAI client...")
    openai_client = OpenAI(api_key=api_key)
    logger.debug("Client initialization successful")
except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

app = Flask(__name__,
            static_folder='public',
            template_folder='public')

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
    
    # If it's not a static file, forward to API routes
    return jsonify({"error": "File not found"}), 404

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "ok",
        "openai_client": openai_client is not None,
        "api_key_present": bool(api_key)
    })

# Avoid circular imports by conditionally importing API routes
try:
    import app as fastapi_app
    logger.debug("Successfully imported FastAPI app")
except ImportError as e:
    logger.warning(f"Could not import FastAPI app: {e}")
except Exception as e:
    logger.error(f"Error importing FastAPI app: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"\n🚀 Starting Flask server at http://0.0.0.0:{port}")
    logger.info("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=port, debug=True)