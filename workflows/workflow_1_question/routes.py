from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Optional
from pathlib import Path
import traceback
import json
from shared.services.gpt_prompt import render_template, send_prompt
from workflows.workflow_1_question.logic import generate_question_components
from workflows.workflow_1_question.schema import TopicRequest, PrepareMaterialsRequest

router = APIRouter()

# Set up templates
templates_path = Path(__file__).parent.parent.parent / "public"
templates = Jinja2Templates(directory=str(templates_path))

# Add a new endpoint for preparing materials (called when the user clicks "Start Writing")
@router.post("/workflow_1_question/prepare_materials")
async def prepare_materials(request: PrepareMaterialsRequest) -> Dict:
    """
    Prepare learning materials based on the generated question
    
    This endpoint is called when the user clicks "Start Writing" after
    generating a question. It prepares additional materials like outline,
    vocabulary suggestions, and sentence suggestions.
    """
    try:
        print(f"Preparing materials for question: {request.question[:50]}...")
        
        # Step 2: Generate the outline based on the question
        print("[Question Generator] Preparing outline prompt...")
        outline_template = "prompt_writing/prompt_outline.txt"
        outline_prompt = render_template(outline_template,
                               question=request.question,
                               band=request.band)
        
        outline_response = await send_prompt(
            prompt=outline_prompt,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=4000
        )
        print("[Question Generator] Outline generated")
        
        # Step 3: Generate vocabulary suggestions
        print("[Question Generator] Preparing vocabulary prompt...")
        vocab_template = "prompt_writing/prompt_vocab.txt"
        vocab_prompt = render_template(vocab_template,
                             topic=request.topic,
                             band=request.band)
        
        vocab_response = await send_prompt(
            prompt=vocab_prompt,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=4000
        )
        print("[Question Generator] Vocabulary generated")
        
        # Step 4: Generate sentence suggestions
        print("[Question Generator] Preparing sentence prompt...")
        sentence_template = "prompt_writing/prompt_sentence.txt"
        sentence_prompt = render_template(sentence_template,
                                topic=request.topic,
                                band=request.band)
        
        sentence_response = await send_prompt(
            prompt=sentence_prompt,
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=4000
        )
        print("[Question Generator] Sentence structures generated")
        
        # Compile the final result
        result = {
            "status": "success",
            "question": request.question,
            "outline": outline_response,
            "vocabulary_suggestions": vocab_response,
            "sentence_suggestions": sentence_response,
            "topic": request.topic,
            "band": request.band,
            "task_type": request.task_type,
            "time_limit": request.time_limit
        }
        
        print("[Question Generator] Successfully generated all components")
        return result
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error preparing materials: {str(e)}")
        print(error_trace)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "traceback": error_trace
            }
        )

# Add a GET endpoint to serve the UI
@router.get("/workflow_1_question", response_class=HTMLResponse)
async def get_question_generator_page(request: Request):
    """Render the question generator UI page"""
    print("Serving question generator page")
    return templates.TemplateResponse(
        "setting.html",  # Updated to use setting.html instead of question.html
        {"request": request}
    )

@router.post("/workflow_1_question/generate")
async def generate_question(request: TopicRequest) -> Dict:
    """
    Generate an IELTS Writing question based on topic and band score
    
    This has been modified to only generate the question part first,
    and then generate the rest of the components later when the user
    clicks "Start Writing"
    """
    try:
        print(f"Received question generation request: topic={request.topic}, band={request.band}, task_type={request.task_type}")
        
        if not request.topic or not request.band:
            print("Missing required fields: topic or band")
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": "Topic and band score are required"
                }
            )
        
        # STEP 1: ONLY GENERATE THE QUESTION FIRST
        try:
            print("[Question Generator] Preparing question prompt...")
            template_name = "prompt_writing/prompt_question.txt"
            question_prompt = render_template(template_name, 
                                  topic=request.topic, 
                                  band=request.band)
            print(f"[Question Generator] Question template rendered, length: {len(question_prompt)} chars")
            
            # Send question prompt to GPT
            print("[Question Generator] Sending question prompt to GPT...")
            question_response = await send_prompt(
                prompt=question_prompt,
                model="gpt-4o-mini",
                temperature=0.2,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse question response
            question_data = json.loads(question_response)
            if "error" in question_data:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "error": question_data["error"],
                        "details": question_data.get("details", "")
                    }
                )
                
            # Extract the question 
            question_text = question_data.get("question", "")
            if not question_text:
                return JSONResponse(
                    status_code=500,
                    content={
                        "status": "error",
                        "error": "No question was generated from the API"
                    }
                )
                
            print(f"[Question Generator] Question generated: {question_text[:50]}...")
            
            # Return ONLY the question to the frontend
            # When the user clicks "Start Writing", the frontend will call
            # the prepare_materials endpoint to generate the rest of the materials
            return {
                "status": "success",
                "question": question_text,
                "topic": request.topic,
                "band": request.band,
                "task_type": "Writing Task 1" if request.task_type == "TASK1" else "Writing Task 2"
            }
            
        except json.JSONDecodeError as e:
            print(f"[Question Generator] Failed to parse JSON: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error": f"Invalid JSON in API response: {str(e)}",
                    "raw_response": question_response
                }
            )
            
        except Exception as api_error:
            print(f"[Question Generator] API call error: {api_error}")
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "error": f"API call failed: {str(api_error)}",
                    "traceback": traceback.format_exc()
                }
            )
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error generating question: {str(e)}")
        print(error_trace)
        
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "traceback": error_trace
            }
        )