from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pathlib import Path
import traceback

from .schema import GradingRequest, GradingResponse
from .logic import process_grading_request

# Create router
router = APIRouter(prefix="/workflow_2_grading", tags=["grading"])

# Templates setup - use the public folder for templates
templates_path = Path(__file__).parent.parent.parent / "public"
templates = Jinja2Templates(directory=str(templates_path))

# Removed router-level exception handlers as they are not supported by APIRouter
# These are handled at the app level in app.py instead

@router.post("/analyze", response_model=GradingResponse)
async def analyze_essay(request: GradingRequest):
    """
    Analyze and grade an IELTS Writing Task 2 essay
    
    This endpoint accepts an essay, question, and type, then:
    1. Analyzes the essay using official IELTS criteria
    2. Provides detailed feedback and scores
    3. Highlights sentences as good, wrong, or improvable
    
    Returns:
        Detailed feedback, scores, and highlighted essay
    """
    try:
        print(f"\n[Grading API] Received grading request. Essay length: {len(request.essay)}")
        
        # Check input
        if not request.essay or not request.question:
            print("[Grading API] Missing required fields")
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Essay and question are required fields",
                    "status_code": 400,
                    # Include all required fields for frontend compatibility
                    "feedback": {},
                    "scores": {
                        "Task Response": 0,
                        "Coherence and Cohesion": 0,
                        "Lexical Resource": 0,
                        "Grammatical Range and Accuracy": 0
                    },
                    "average_band": 0,
                    "essay_highlights": "",
                    "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                    "explanations": {"green": [], "red": [], "yellow": []}
                }
            )
        
        # Process the request through our workflow
        print("[Grading API] Processing request...")
        result = await process_grading_request(request)
        
        # Check for errors
        if "error" in result:
            status_code = result.get("status_code", 500)
            error_msg = result.get("error", "Unknown error")
            print(f"[Grading API] Error in result: {error_msg} (status {status_code})")
            
            # For JSONResponse, make sure all required fields are included
            response_content = {
                "error": error_msg,
                "details": result.get("details", ""),
                "traceback": result.get("traceback", ""),
                # Include all required fields for frontend compatibility
                "feedback": result.get("feedback", {}),
                "scores": result.get("scores", {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                }),
                "average_band": result.get("average_band", 0),
                "essay_highlights": result.get("essay_highlights", request.essay),
                "highlighted_sentences": result.get("highlighted_sentences", {"green": [], "red": [], "yellow": []}),
                "explanations": result.get("explanations", {"green": [], "red": [], "yellow": []})
            }
            
            return JSONResponse(
                status_code=status_code,
                content=response_content
            )
        
        print("[Grading API] Grading completed successfully")
        # Return successful response
        return result
    
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"[Grading API] Unexpected error: {e}")
        print(error_trace)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": f"Failed to process essay grading: {e}",
                "traceback": error_trace,
                "details": "An unexpected error occurred while processing your request",
                # Include all required fields for frontend compatibility
                "feedback": {},
                "scores": {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "average_band": 0,
                "essay_highlights": request.essay,
                "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
        )


@router.get("/", response_class=HTMLResponse)
async def get_grading_page(request: Request):
    """Render the grading UI page"""
    print("[Grading API] Serving grading page")
    return templates.TemplateResponse(
        "grading.html",
        {"request": request}
    ) 