from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
from pathlib import Path

# Import the workflow routers
from workflows.workflow_1_question import router as question_router
from workflows.workflow_2_grading import router as grading_router

# Create the FastAPI app
app = FastAPI(
    title="IELTS Writing AI",
    description="AI-powered IELTS Writing Task 2 practice and grading",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handlers for the entire app
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    if request.url.path.startswith("/workflow_2_grading"):
        # For grading API, return JSON with complete structure
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "detail": str(exc),
                "feedback": {},
                "scores": {"task": 0, "coherence": 0, "lexical": 0, "grammar": 0},
                "average_band": 0,
                "essay_highlights": "",
                "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
        )
    # For other routes, return standard error
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "detail": str(exc)}
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    if request.url.path.startswith("/workflow_2_grading"):
        # For grading API, return JSON with complete structure
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP error",
                "detail": str(exc.detail),
                "feedback": {},
                "scores": {"task": 0, "coherence": 0, "lexical": 0, "grammar": 0},
                "average_band": 0,
                "essay_highlights": "",
                "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
        )
    # For other routes, let FastAPI handle it normally
    raise exc

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    error_trace = traceback.format_exc()
    if request.url.path.startswith("/workflow_2_grading"):
        # For grading API, return JSON with complete structure
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "traceback": error_trace,
                "feedback": {},
                "scores": {"task": 0, "coherence": 0, "lexical": 0, "grammar": 0},
                "average_band": 0,
                "essay_highlights": "",
                "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
        )
    # For other routes, return standard error
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "traceback": error_trace
        }
    )

# Set up templates
templates = Jinja2Templates(directory="public")

# Include the workflow routers
app.include_router(question_router)
app.include_router(grading_router)

# Mount static files AFTER including routers
app.mount("/js", StaticFiles(directory=Path("public/js")), name="js")
app.mount("/css", StaticFiles(directory=Path("public/css")), name="css")
app.mount("/static", StaticFiles(directory=Path("public"), html=True), name="static")

# Serve HTML pages
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/vocabulary-coming-soon.html", response_class=HTMLResponse)
async def vocabulary_coming_soon(request: Request):
    return templates.TemplateResponse("vocabulary-coming-soon.html", {"request": request})

@app.get("/progress-coming-soon.html", response_class=HTMLResponse)
async def progress_coming_soon(request: Request):
    return templates.TemplateResponse("progress-coming-soon.html", {"request": request})

@app.get("/account.html", response_class=HTMLResponse)
async def my_account(request: Request):
    return templates.TemplateResponse("account.html", {"request": request})

@app.get("/practice.html", response_class=HTMLResponse)
async def practice_page(request: Request):
    return templates.TemplateResponse("practice.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    
    # Run the FastAPI app with uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )