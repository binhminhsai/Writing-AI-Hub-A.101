from typing import Dict, Any
import traceback
import time

from .agents import GradingAgent
from .schema import GradingRequest, GradingResponse


async def process_grading_request(request: GradingRequest) -> Dict[str, Any]:
    """
    Process an IELTS essay grading request
    
    Args:
        request: The grading request containing essay, question, and types
        
    Returns:
        A dictionary with grading results including feedback, scores, and highlights
    """
    start_time = time.time()
    request_id = f"req-{int(start_time)}"
    print(f"\n[Grading:{request_id}] Starting grading request")
    
    # Input validation
    essay = request.essay.strip()
    question = request.question.strip()
    types = request.types.strip()
    
    print(f"[Grading:{request_id}] Essay length: {len(essay)}, Question length: {len(question)}, Type: {types}")
    
    if not essay or not question:
        print(f"[Grading:{request_id}] Missing required fields: essay={bool(essay)}, question={bool(question)}")
        return {
            "error": "Essay and question are required fields",
            "status_code": 400,
            # Add required fields for frontend compatibility
            "feedback": {},
            "scores": {"Task Response": 0, "Coherence and Cohesion": 0, "Lexical Resource": 0, "Grammatical Range and Accuracy": 0},
            "average_band": 0,
            "essay_highlights": "",
            "highlighted_sentences": {"green": [], "red": [], "yellow": []},
            "explanations": {"green": [], "red": [], "yellow": []}
        }
    
    # Initialize the grading agent
    try:
        print(f"[Grading:{request_id}] Initializing grading agent...")
        agent = GradingAgent()
        print(f"[Grading:{request_id}] Agent initialized successfully")
    except Exception as e:
        print(f"[Grading:{request_id}] Error initializing agent: {e}")
        print(traceback.format_exc())
        return {
            "error": f"Failed to initialize grading agent: {e}",
            "traceback": traceback.format_exc(),
            "status_code": 500,
            # Add required fields for frontend compatibility
            "feedback": {},
            "scores": {"Task Response": 0, "Coherence and Cohesion": 0, "Lexical Resource": 0, "Grammatical Range and Accuracy": 0},
            "average_band": 0,
            "essay_highlights": essay,
            "highlighted_sentences": {"green": [], "red": [], "yellow": []},
            "explanations": {"green": [], "red": [], "yellow": []}
        }
    
    try:
        # Run the grading workflow
        print(f"[Grading:{request_id}] Running grading workflow...")
        result = await agent.run(question, essay, types)
        print(f"[Grading:{request_id}] Grading workflow completed")
        
        # Check for errors in the result
        if "error" in result and result["error"]:
            print(f"[Grading:{request_id}] Error in grading result: {result['error']}")
            # Make sure to include all required fields even when an error occurs
            # This ensures the frontend can still display something
            error_result = {
                "error": result["error"],
                "details": result.get("details", "Unknown error"),
                "status_code": 500,
                "feedback": result.get("feedback", {}),
                "scores": {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "average_band": 0,
                "essay_highlights": essay,
                "highlighted_sentences": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
            # Copy any existing fields from the result
            for key in ["feedback", "scores", "average_band", "essay_highlights", 
                      "highlighted_sentences", "explanations"]:
                if key in result and result[key]:
                    error_result[key] = result[key]
            return error_result
        
        # Map the scores to match our schema format
        if "scores" in result and result["scores"]:
            scores = result["scores"]
            print(f"[Grading:{request_id}] Raw scores: {scores}")
            # Handle potential missing fields
            mapped_scores = {
                "Task Response": scores.get("Task Response", 0),
                "Coherence and Cohesion": scores.get("Coherence and Cohesion", 0),
                "Lexical Resource": scores.get("Lexical Resource", 0),
                "Grammatical Range and Accuracy": scores.get("Grammatical Range and Accuracy", 0)
            }
            result["scores"] = mapped_scores
            print(f"[Grading:{request_id}] Mapped scores: {mapped_scores}")
        else:
            print(f"[Grading:{request_id}] No scores in result")
            result["scores"] = {
                "Task Response": 0,
                "Coherence and Cohesion": 0,
                "Lexical Resource": 0,
                "Grammatical Range and Accuracy": 0
            }
        
        # Ensure all required fields exist in the result
        required_fields = ["feedback", "scores", "average_band", "essay_highlights", "highlighted_sentences", "explanations"]
        for field in required_fields:
            if field not in result:
                print(f"[Grading:{request_id}] Missing field in result: {field}")
                if field == "feedback":
                    result[field] = {}
                elif field == "scores":
                    result[field] = {
                        "Task Response": 0,
                        "Coherence and Cohesion": 0,
                        "Lexical Resource": 0,
                        "Grammatical Range and Accuracy": 0
                    }
                elif field == "average_band":
                    result[field] = 0
                elif field == "essay_highlights":
                    result[field] = essay
                elif field == "highlighted_sentences":
                    result[field] = {"green": [], "red": [], "yellow": []}
                elif field == "explanations":
                    result[field] = {"green": [], "red": [], "yellow": []}
        
        processing_time = time.time() - start_time
        print(f"[Grading:{request_id}] Processing completed in {processing_time:.2f} seconds")
        return result
        
    except Exception as e:
        # Log the error
        print(f"[Grading:{request_id}] Error in grading workflow: {e}")
        print(traceback.format_exc())
        
        processing_time = time.time() - start_time
        print(f"[Grading:{request_id}] Processing failed after {processing_time:.2f} seconds")
        
        # Return error response with all required fields to prevent frontend errors
        return {
            "error": f"Failed to process essay grading: {e}",
            "traceback": traceback.format_exc(),
            "status_code": 500,
            "feedback": {},
            "scores": {
                "Task Response": 0,
                "Coherence and Cohesion": 0,
                "Lexical Resource": 0,
                "Grammatical Range and Accuracy": 0
            },
            "average_band": 0,
            "essay_highlights": essay,
            "highlighted_sentences": {"green": [], "red": [], "yellow": []},
            "explanations": {"green": [], "red": [], "yellow": []}
        } 