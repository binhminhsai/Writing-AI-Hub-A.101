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
        # Import các module Workflow
        from workflows.workflow_1_question.routes import router as question_router
        from workflows.workflow_1_question.schema import TopicRequest, PrepareMaterialsRequest
        from workflows.workflow_2_grading.routes import router as grading_router
        logger.debug("Successfully imported FastAPI app and workflow routers")
    except ImportError as e:
        logger.warning(f"Could not import FastAPI app or routers: {e}")
    except Exception as e:
        logger.error(f"Error importing FastAPI app or routers: {e}")
    
    # Tạo middleware cho các workflow endpoints trong Flask
    @app.route('/workflow_1_question/generate', methods=['GET', 'POST'])
    def workflow_1_generate():
        # Kiểm tra nếu là phương thức GET, trả về một phản hồi đơn giản
        if request.method == 'GET':
            return jsonify({"message": "This endpoint accepts POST requests for question generation"}), 200
            
        # Nhận dữ liệu JSON từ request POST
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "error": "No JSON data provided"}), 400
        
        # Log dữ liệu nhận được
        logger.debug(f"Received data: {data}")
        
        # Tạo đối tượng TopicRequest từ dữ liệu JSON
        try:
            topic_request = TopicRequest(**data)
            
            # Gọi hàm async bằng cách sử dụng asyncio
            import asyncio
            from workflows.workflow_1_question.routes import generate_question
            
            # Tạo event loop và chạy hàm async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(generate_question(topic_request))
            
            # Trả về kết quả dưới dạng JSON
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in workflow_1_generate: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
    @app.route('/workflow_1_question/prepare_materials', methods=['GET', 'POST'])
    def workflow_1_prepare_materials():
        # Kiểm tra nếu là phương thức GET, trả về một phản hồi đơn giản
        if request.method == 'GET':
            return jsonify({"message": "This endpoint accepts POST requests for materials preparation"}), 200
            
        # Nhận dữ liệu JSON từ request POST
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "error": "No JSON data provided"}), 400
        
        # Log dữ liệu nhận được
        logger.debug(f"Received data for prepare_materials: {data}")
        
        # Tạo đối tượng PrepareMaterialsRequest từ dữ liệu JSON
        try:
            materials_request = PrepareMaterialsRequest(**data)
            
            # Gọi hàm async bằng cách sử dụng asyncio
            import asyncio
            from workflows.workflow_1_question.routes import prepare_materials
            
            # Tạo event loop và chạy hàm async
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(prepare_materials(materials_request))
            
            # Trả về kết quả dưới dạng JSON
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in workflow_1_prepare_materials: {e}")
            return jsonify({"status": "error", "error": str(e)}), 500
    
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
        
    @app.route('/progress-coming-soon.html')
    def progress_coming_soon():
        return send_from_directory('public', 'progress-coming-soon.html')
        
    @app.route('/vocabulary-coming-soon.html')
    def vocabulary_coming_soon():
        return send_from_directory('public', 'vocabulary-coming-soon.html')
    
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
        
    @app.get("/progress-coming-soon.html")
    async def get_progress_coming_soon():
        return FileResponse('public/progress-coming-soon.html')
        
    @app.get("/vocabulary-coming-soon.html")
    async def get_vocabulary_coming_soon():
        return FileResponse('public/vocabulary-coming-soon.html')
    
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