from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Dict, Optional
from pathlib import Path
import traceback
from workflows.workflow_1_question.logic import generate_question_components
from workflows.workflow_1_question.schema import TopicRequest

router = APIRouter()

# Set up templates
templates_path = Path(__file__).parent.parent.parent / "public"
templates = Jinja2Templates(directory=str(templates_path))

# Add a GET endpoint to serve the UI
@router.get("/workflow_1_question", response_class=HTMLResponse)
async def get_question_generator_page(request: Request):
    """Render the question generator UI page"""
    print("Serving question generator page")
    return templates.TemplateResponse(
        "question.html",  # This should be in public folder
        {"request": request}
    )

@router.post("/workflow_1_question/generate")
async def generate_question(request: TopicRequest) -> Dict:
    """
    Generate an IELTS Writing question based on topic and band score
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
        
        # Generate the question components
        print("Calling generate_question_components...")
        result = await generate_question_components(
            request.topic,
            request.band,
            request.task_type
        )
        
        # Check for errors in the result
        if result.get("status") == "error":
            print(f"Error in question generation: {result.get('error')}")
            return JSONResponse(
                status_code=500,
                content=result
            )
        
        print(f"Generated question successfully. Status: {result.get('status', 'unknown')}")
        return result
        
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