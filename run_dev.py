import os
import sys
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    # Check for OpenAI API key
    api_key = os.environ.get("OPENAI_API_KEY", "")
    
    # Print status of API key
    if not api_key:
        print("\n⚠️ WARNING: No OpenAI API key found in environment variables!")
        print("Please add your API key to the .env file: OPENAI_API_KEY=your-key-here\n")
        
        # Prompt for API key
        api_key = input("Enter your OpenAI API key: ").strip()
        if not api_key:
            print("[ERROR] No API key provided. Exiting.")
            sys.exit(1)
        os.environ["OPENAI_API_KEY"] = api_key
    elif len(api_key) < 20:  # Basic length check for API key
        print("\n⚠️ WARNING: OpenAI API key appears to be too short!")
        print("Please check your API key in the .env file\n")
    else:
        print(f"\n✅ OpenAI API key found (starts with: {api_key[:5]}...)")
    
    # Force use of real API - disable mock responses
    os.environ["MOCK_GPT_RESPONSES"] = "false"
    
    # Set default host and port
    host = "0.0.0.0"
    port = 8080
    
    # Run the server
    print(f"\n🚀 Starting server at http://{host}:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        uvicorn.run(
            "app:app",
            host=host,
            port=port,
            reload=True,
            workers=1
        )
    except KeyboardInterrupt:
        print("\n[INFO] Development server stopped")
    except Exception as e:
        print(f"\n[ERROR] Error starting server: {e}")
        sys.exit(1) 