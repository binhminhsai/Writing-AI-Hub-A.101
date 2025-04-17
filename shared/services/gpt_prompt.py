import os
import json
import asyncio
from typing import Dict, Any, Optional, List, Union
from openai import AsyncOpenAI, OpenAIError
from dotenv import load_dotenv
import time

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = None

def init_client():
    global client
    api_key = os.environ.get("OPENAI_API_KEY", "")
    print(f"DEBUG: API key present: {bool(api_key)}, length: {len(api_key) if api_key else 0}")
    if len(api_key) > 15:
        print(f"DEBUG: API key starts with: {api_key[:15]}...")
    else:
        print("DEBUG: API key is too short or empty!")
    
    if not api_key:
        print("WARNING: No OpenAI API key found in environment variables!")
        return False
    
    try:
        print(f"DEBUG: Initializing OpenAI client with 200s timeout...")
        client = AsyncOpenAI(
            api_key=api_key,
            timeout=200.0, # Timeout set to 200 seconds
            max_retries=1  
        )
        print("DEBUG: Client initialization successful")
        return True
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return False

# Initialize on module import
init_client_success = init_client()

async def send_prompt(
    prompt: str,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_tokens: int = 4000,
    response_format: Optional[Dict[str, str]] = None,
    stream: bool = False
) -> str:
    """
    Send a prompt to OpenAI API and get the response
    """
    global client, init_client_success
    
    # Always use real API, never use mock responses
    # We set this in .env and run_dev.py enforces it
    
    try:
        print("\n=== Starting OpenAI API Request ===")
        print(f"Model: {model}")
        print(f"Temperature: {temperature}")
        print(f"Max tokens: {max_tokens}")
        print(f"Response format: {response_format}")
        print(f"Prompt length: {len(prompt)} chars")
        print(f"Prompt first 100 chars: {prompt[:100]}...")
        if len(prompt) > 5000:
            print(f"WARNING: Long prompt detected ({len(prompt)} chars)")
        
        # Ensure we have a client
        if not init_client_success:
            print("Attempting to reinitialize client...")
            init_client_success = init_client()
        
        if not client:
            error_msg = "OpenAI client is not initialized. Check your API key."
            print(f"ERROR: {error_msg}")
            raise Exception("OpenAI client initialization failed.")
        
        # Prepare messages
        messages = [{"role": "user", "content": prompt}]
        
        # Call the API
        try:
            print("Making API call to OpenAI...")
            start_time = time.time()
            
            # <<< Log right before the await >>>
            print("[DEBUG] Awaiting client.chat.completions.create...") 
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
                # Timeout is now configured globally in the client
            )
            
            # <<< Log right after the await if successful >>>
            print("[DEBUG] ** Await completed. Processing response... **") 
            
            end_time = time.time()
            
            # Process the response
            result = response.choices[0].message.content
            print(f"API call successful in {end_time - start_time:.2f} seconds, received {len(result)} chars")
            print(f"Response first 200 chars: {result[:200]}...")
            
            # Validate JSON response if needed
            if response_format and response_format.get('type') == 'json_object':
                try:
                    # Try to parse as JSON to validate
                    parsed_json = json.loads(result)
                    print("Successfully validated JSON response")
                    
                    # Print the top-level keys in the JSON
                    print(f"JSON keys: {list(parsed_json.keys())}")
                    
                    # Validate required sections for each criterion
                    criteria = ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
                    for criterion in criteria:
                        if criterion in parsed_json and isinstance(parsed_json[criterion], dict):
                            # Check if ANY 'Why not +0.5' key exists
                            has_plus_key = any(key.startswith("Why not Band ") and key.endswith(" + 0.5?") for key in parsed_json[criterion])
                            if not has_plus_key:
                                print(f"WARNING: Missing 'Why not Band [score] + 0.5?' in {criterion}")
                                parsed_json[criterion]["Why not Band X + 0.5?"] = "🔼 Missing higher band justification"
                            
                            # Check if ANY 'Why not -0.5' key exists (handle both '-' and '–')
                            has_minus_key = any(key.startswith("Why not Band ") and (key.endswith(" - 0.5?") or key.endswith(" – 0.5?")) for key in parsed_json[criterion])
                            if not has_minus_key:
                                print(f"WARNING: Missing 'Why not Band [score] – 0.5?' in {criterion}")
                                parsed_json[criterion]["Why not Band X – 0.5?"] = "🔽 Missing lower band justification"
                    
                    # Convert back to string AFTER potential additions
                    result = json.dumps(parsed_json)
                    
                    # Check for scores in the JSON
                    if 'scores' in parsed_json:
                        print(f"Scores found in response: {parsed_json['scores']}")
                    
                except json.JSONDecodeError as e:
                    # If parsing fails, wrap the response in a proper JSON structure
                    print(f"WARNING: JSON validation failed: {str(e)}")
                    print(f"Invalid JSON received: {result[:500]}...")
                    
                    # Try to fix common JSON issues
                    result = result.strip()
                    if result.startswith('```json'):
                        result = result[7:].strip()
                    if result.endswith('```'):
                        result = result[:-3].strip()
                    
                    try:
                        # Try parsing again after cleanup
                        json.loads(result)
                        print("JSON successfully fixed and validated")
                    except json.JSONDecodeError:
                        # If still invalid, return a fallback JSON
                        print("Converting to proper JSON format")
                        result = json.dumps({
                            "error": "Invalid JSON response from OpenAI",
                            "feedback": {"raw_response": result},
                            "scores": {
                                "Task Response": 0,
                                "Coherence and Cohesion": 0,
                                "Lexical Resource": 0,
                                "Grammatical Range and Accuracy": 0
                            },
                            "average_band": 0,
                            "highlighted_essay_html": "",
                            "highlights": {"green": [], "red": [], "yellow": []},
                            "explanations": {"green": [], "red": [], "yellow": []},
                            "Task Response": {
                                "Strengths": [],
                                "Weaknesses": [],
                                "Band Score Justification": "Band 0.0 - Invalid response",
                                "Why not Band X + 0.5?": "🔼 Unable to assess - Invalid response",
                                "Why not Band X – 0.5?": "🔽 Unable to assess - Invalid response"
                            },
                            "Coherence and Cohesion": {
                                "Strengths": [],
                                "Weaknesses": [],
                                "Band Score Justification": "Band 0.0 - Invalid response",
                                "Why not Band X + 0.5?": "🔼 Unable to assess - Invalid response",
                                "Why not Band X – 0.5?": "🔽 Unable to assess - Invalid response"
                            },
                            "Lexical Resource": {
                                "Strengths": [],
                                "Weaknesses": [],
                                "Band Score Justification": "Band 0.0 - Invalid response",
                                "Why not Band X + 0.5?": "🔼 Unable to assess - Invalid response",
                                "Why not Band X – 0.5?": "🔽 Unable to assess - Invalid response"
                            },
                            "Grammatical Range and Accuracy": {
                                "Strengths": [],
                                "Weaknesses": [],
                                "Band Score Justification": "Band 0.0 - Invalid response",
                                "Why not Band X + 0.5?": "🔼 Unable to assess - Invalid response",
                                "Why not Band X – 0.5?": "🔽 Unable to assess - Invalid response"
                            }
                        })
            
            return result
            
        except OpenAIError as api_error:
            # <<< Log specific timeout error >>>
            if isinstance(api_error, asyncio.TimeoutError) or "timed out" in str(api_error).lower():
                 print(f"ERROR: OpenAI API call timed out after configured duration.")
            error_msg = f"OpenAI API Error: {str(api_error)}"
            print(f"ERROR: {error_msg}")
            # Provide more detailed error info
            if hasattr(api_error, 'headers'):
                print(f"Error headers: {api_error.headers}")
            if hasattr(api_error, 'status_code'):
                print(f"Error status code: {api_error.status_code}")
            if hasattr(api_error, 'response'):
                print(f"Error response: {api_error.response}")
            raise api_error
            
        except asyncio.TimeoutError:
            # Catch asyncio timeout specifically if not caught by OpenAIError
             print(f"ERROR: OpenAI API call hit asyncio.TimeoutError.")
             raise Exception("OpenAI API call timed out.")
            
        except Exception as e:
            error_msg = f"Error during API call: {str(e)}"
            print(f"ERROR: {error_msg}")
            raise e
            
    except Exception as e:
        error_msg = f"Error in send_prompt: {str(e)}"
        print(f"ERROR: {error_msg}")
        raise e
    finally:
        print("=== Finished OpenAI API Request ===\n")

# If using async in non-async context (like Flask)
def sync_send_prompt(*args, **kwargs) -> str:
    """Synchronous version of send_prompt for non-async contexts"""
    return asyncio.run(send_prompt(*args, **kwargs))

def render_template(template_name: str, **kwargs) -> str:
    """
    Load a template and render it with the provided variables
    """
    try:
        template_path = os.path.join('shared/templates', template_name)
        with open(template_path, 'r', encoding='utf-8') as file:
            template = file.read()
        return template.format(**kwargs)
    except Exception as e:
        raise Exception(f"Template error ({template_name}): {str(e)}")

def load_sample(sample_name: str) -> str:
    """
    Load a sample file
    """
    try:
        sample_path = os.path.join('shared/templates/samples', f'{sample_name}.txt')
        with open(sample_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Sample loading error: {str(e)}")
