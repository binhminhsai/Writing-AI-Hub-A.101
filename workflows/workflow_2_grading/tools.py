import json
import os
import traceback  # Added explicit import for traceback
from typing import Dict, Any

from .constants import (
    PROMPT_ANALYZE,
    PROMPT_HIGHLIGHT,
    PROMPT_SCORE,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    read_prompt,
    get_band_descriptors,
    get_band_descriptors_memory
)

# Import send_prompt function from the merged module
from shared.services.gpt_prompt import send_prompt


class Tool1AnalyzeAndScore:
    """Tool to analyze and score IELTS essays based on official criteria"""
    
    def __init__(self, model="gpt-4o-mini", temperature=0.1):
        self.model = model
        self.temperature = temperature
        try:
            print("Loading Tool1 templates...")
            self.analyze_prompt_template = read_prompt(PROMPT_ANALYZE)
            self.score_prompt_template = read_prompt(PROMPT_SCORE)
            self.band_descriptors = get_band_descriptors_memory()
            print("Tool1 templates loaded successfully")
        except Exception as e:
            print(f"Error initializing Tool1 templates: {e}")
            print(traceback.format_exc())
            raise Exception("Failed to initialize Tool1 - templates not loaded correctly")

    def extract_band_score(self, justification: str) -> float:
        """Extract band score from justification text"""
        if not justification:
            return 0.0
        
        try:
            # Look for patterns like "Band 7" or "Band 7.5"
            import re
            matches = re.findall(r'Band\s+(\d+\.?\d*)', justification)
            if matches:
                print(f"[Tool1] Found band score: {matches[0]}")
                return float(matches[0])
            
            # Try alternative pattern
            matches = re.findall(r'(\d+\.?\d*)', justification)
            if matches:
                print(f"[Tool1] Found numeric score: {matches[0]}")
                return float(matches[0])
            
            print(f"[Tool1] No score found in: {justification}")
            return 0.0
        except Exception as e:
            print(f"[Tool1] Error extracting score: {str(e)}")
            return 0.0

    async def run(self, question: str, essay: str, types: str) -> Dict[str, Any]:
        """Run the analysis and scoring on an essay"""
        print(f"\n[Tool1] Starting essay analysis. Essay length: {len(essay)} chars")
        print(f"[Tool1] Question: {question[:100]}...")
        print(f"[Tool1] Essay type: {types}")
        
        # Input validation
        if not essay or len(essay.strip()) < 50:
            print("[Tool1] Essay too short or empty")
            return {
                "feedback": {"error": "Essay must be at least 50 words long"},
                "scores": {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "average_band": 0
            }
        
        try:
            # 1. Analyze essay with detailed feedback
            print("[Tool1] Preparing analysis prompt...")
            analyze_prompt = self.analyze_prompt_template.replace(
                "{{ types }}", types
            ).replace(
                "{{ question }}", question
            ).replace(
                "{{ essay }}", essay
            ).replace(
                "{{ ielts_criteria }}", self.band_descriptors
            )
            
            # Call OpenAI API for analysis
            print(f"[Tool1] Calling API for essay analysis using model: {self.model}")
            try:
                feedback_response = await send_prompt(
                    prompt=analyze_prompt,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=4000,
                    response_format={"type": "json_object"}
                )
                print(f"[Tool1] Received analysis response: {len(feedback_response)} chars")
                print(f"[Tool1] Response preview: {feedback_response[:200]}...")
            except Exception as api_error:
                print(f"[Tool1] Analysis API error: {str(api_error)}")
                return {
                    "error": f"Analysis failed: {str(api_error)}",
                    "feedback": {},
                    "scores": {
                        "Task Response": 0,
                        "Coherence and Cohesion": 0,
                        "Lexical Resource": 0,
                        "Grammatical Range and Accuracy": 0
                    },
                    "average_band": 0
                }
            
            # Parse feedback JSON
            try:
                print("[Tool1] Parsing analysis JSON response...")
                print(f"[Tool1] Full response string before parsing:\n{feedback_response}")
                feedback = json.loads(feedback_response)
                print("[Tool1] Successfully parsed analysis JSON")
                print(f"[Tool1] Parsed feedback keys: {list(feedback.keys())}")
                
                # Debug the feedback structure
                # print(f"[Tool1] Feedback keys: {list(feedback.keys())}") # Original log, can be removed or kept
                
                # Check if scores are directly provided in the response
                if "scores" in feedback:
                    print("[Tool1] Found direct scores in response")
                    scores = feedback["scores"]
                    # Ensure scores are numeric
                    for key, value in scores.items():
                        if isinstance(value, str):
                            try:
                                scores[key] = float(value)
                            except ValueError:
                                scores[key] = 0.0
                    
                    # Calculate average
                    avg_band = sum(float(v) for v in scores.values()) / len(scores)
                    avg_band = round(avg_band * 2) / 2  # Round to nearest 0.5
                    
                    print(f"[Tool1] Direct scores: {scores}")
                    print(f"[Tool1] Average band: {avg_band}")
                    
                    return {
                        "feedback": feedback,
                        "scores": scores,
                        "average_band": avg_band
                    }
                
                # Validate feedback structure for criteria-based scoring
                criteria = ["Task Response", "Coherence and Cohesion", "Lexical Resource", "Grammatical Range and Accuracy"]
                for criterion in criteria:
                    if criterion not in feedback:
                        print(f"[Tool1] Missing criterion: {criterion}")
                        feedback[criterion] = {
                            "Strengths": [],
                            "Weaknesses": [],
                            "Band Score Justification": f"Band 0.0 - Unable to assess {criterion}",
                            "Why not Band X + 0.5?": "🔼 Unable to assess higher band potential",
                            "Why not Band X – 0.5?": "🔽 Unable to assess lower band justification"
                        }
                    elif not isinstance(feedback[criterion], dict):
                        print(f"[Tool1] Invalid format for criterion: {criterion}")
                        feedback[criterion] = {
                            "Strengths": [],
                            "Weaknesses": [],
                            "Band Score Justification": f"Band 0.0 - Invalid format for {criterion}",
                            "Why not Band X + 0.5?": "🔼 Unable to assess higher band potential",
                            "Why not Band X – 0.5?": "🔽 Unable to assess lower band justification"
                        }
                    elif "Band Score Justification" not in feedback[criterion]:
                        print(f"[Tool1] Missing Band Score Justification for: {criterion}")
                        feedback[criterion]["Band Score Justification"] = f"Band 0.0 - Missing justification for {criterion}"
                        feedback[criterion]["Why not Band X + 0.5?"] = "🔼 Unable to assess higher band potential"
                        feedback[criterion]["Why not Band X – 0.5?"] = "🔽 Unable to assess lower band justification"
                    
                    # Print what we found
                    justification = feedback[criterion].get("Band Score Justification", "")
                    print(f"[Tool1] {criterion} justification: {justification[:100]}...")
                
            except json.JSONDecodeError as json_error:
                print(f"[Tool1] Invalid JSON from analysis: {str(json_error)}")
                print(f"[Tool1] Raw response: {feedback_response}")
                return {
                    "error": f"Invalid analysis response: {str(json_error)}",
                    "feedback": {},
                    "scores": {
                        "Task Response": 0,
                        "Coherence and Cohesion": 0,
                        "Lexical Resource": 0,
                        "Grammatical Range and Accuracy": 0
                    },
                    "average_band": 0
                }
            
            # Extract scores from justifications
            scores = {}
            for criterion in criteria:
                justification = feedback[criterion].get("Band Score Justification", "")
                scores[criterion] = self.extract_band_score(justification)
                print(f"[Tool1] Extracted score for {criterion}: {scores[criterion]}")
            
            # Calculate average band score
            if scores and any(scores.values()):
                total = sum(scores.values())
                avg_band = round(total / len(scores) * 2) / 2  # Round to nearest 0.5
                print(f"[Tool1] Calculated average band: {avg_band}")
            else:
                avg_band = 0
                print("[Tool1] No scores available, setting average to 0")
            
            # Final result
            final_result = {
                "feedback": feedback,
                "scores": scores,
                "average_band": avg_band
            }
            
            print(f"[Tool1] Final result scores: {scores}")
            print(f"[Tool1] Final result average: {avg_band}")
            
            return final_result
            
        except Exception as e:
            print(f"[Tool1] Error in analysis: {str(e)}")
            print(traceback.format_exc())
            return {
                "error": f"Analysis failed: {str(e)}",
                "feedback": {},
                "scores": {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                },
                "average_band": 0
            }


class Tool2HighlightEssay:
    """Tool to highlight and explain sentences in the essay"""
    
    def __init__(self, model="gpt-4o-mini", temperature=0.1):
        self.model = model
        self.temperature = temperature
        try:
            print("Loading Tool2 templates...")
            self.highlight_prompt_template = read_prompt(PROMPT_HIGHLIGHT)
            print("Tool2 templates loaded successfully")
        except Exception as e:
            print(f"Error initializing Tool2 templates: {e}")
            print(traceback.format_exc())
            # Use simple fallback template
            self.highlight_prompt_template = """
            Analyze this essay:
            
            {{ essay }}
            
            For each sentence, determine if it is:
            - Good (highlight green)
            - Wrong (highlight red)
            - Improvable (highlight yellow)
            
            Return as JSON with:
            - highlighted_essay_html: The essay with HTML spans for coloring
            - highlights: Lists of sentences by color category
            - explanations: Detailed feedback for each sentence
            """
    
    async def run(self, essay: str) -> Dict[str, Any]:
        """Run the highlighting and explanation on an essay"""
        print(f"\n[Tool2] Starting essay highlighting. Essay length: {len(essay)} chars")
        
        # Input validation
        if not essay:
            print("[Tool2] Empty essay")
            return {
                "highlighted_essay_html": "",
                "highlights": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            }
        
        try:
            # Prepare highlight prompt
            print("[Tool2] Preparing highlighting prompt...")
            highlight_prompt = self.highlight_prompt_template.replace(
                "{{ essay }}", essay
            )
            
            # Print first part of prompt for debugging
            print(f"[Tool2] Highlight prompt (first 200 chars): {highlight_prompt[:200]}...")
            
            # Call OpenAI API for highlighting
            print("[Tool2] Calling API for essay highlighting...")
            highlight_response = await send_prompt(
                prompt=highlight_prompt,
                model=self.model,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            # Parse highlight JSON
            try:
                print(f"[Tool2] Parsing highlight response (first 200 chars): {highlight_response[:200]}...")
                result = json.loads(highlight_response)
                print("[Tool2] Successfully parsed highlighting JSON")
                
                # Validate result structure
                if "highlighted_essay_html" not in result:
                    print("[Tool2] Missing highlighted_essay_html in response")
                    result["highlighted_essay_html"] = essay
                if "highlights" not in result:
                    print("[Tool2] Missing highlights in response")
                    result["highlights"] = {"green": [], "red": [], "yellow": []}
                if "explanations" not in result:
                    print("[Tool2] Missing explanations in response")
                    result["explanations"] = {"green": [], "red": [], "yellow": []}
                
                # Validate HTML spans in highlighted_essay_html
                if not any(color in result["highlighted_essay_html"].lower() for color in ["green", "red", "orange"]):
                    print("[Tool2] No color spans found in highlighted_essay_html")
                    # Try to rebuild from highlights
                    html = essay
                    for color, sentences in result["highlights"].items():
                        for sentence in sentences:
                            span_color = "orange" if color == "yellow" else color
                            html = html.replace(sentence, f"<span style='color:{span_color}'>{sentence}</span>")
                    result["highlighted_essay_html"] = html
                
                # Ensure all highlights have explanations
                for color in ["green", "red", "yellow"]:
                    if color not in result["highlights"]:
                        result["highlights"][color] = []
                    if color not in result["explanations"]:
                        result["explanations"][color] = []
                    
                    # Match number of highlights and explanations
                    if len(result["highlights"][color]) > len(result["explanations"][color]):
                        print(f"[Tool2] Missing explanations for {color} highlights")
                        # Add default explanations
                        while len(result["explanations"][color]) < len(result["highlights"][color]):
                            if color == "green":
                                result["explanations"][color].append({
                                    "sentence": result["highlights"][color][len(result["explanations"][color])],
                                    "reason": "Good sentence structure and vocabulary"
                                })
                            elif color == "red":
                                result["explanations"][color].append({
                                    "sentence": result["highlights"][color][len(result["explanations"][color])],
                                    "error": "Potential error detected",
                                    "correction": result["highlights"][color][len(result["explanations"][color])],
                                    "reason": "Needs review for accuracy"
                                })
                            else:  # yellow
                                result["explanations"][color].append({
                                    "sentence": result["highlights"][color][len(result["explanations"][color])],
                                    "issue": "Could be improved",
                                    "improved": result["highlights"][color][len(result["explanations"][color])],
                                    "reason": "Consider enhancing for better clarity"
                                })
                
                return result
                
            except json.JSONDecodeError:
                print(f"[Tool2] Invalid JSON response from highlighting: {highlight_response[:200]}...")
                return {
                    "highlighted_essay_html": essay,
                    "highlights": {"green": [], "red": [], "yellow": []},
                    "explanations": {"green": [], "red": [], "yellow": []}
                }
                
        except Exception as e:
            print(f"[Tool2] Error processing highlights: {e}")
            print(traceback.format_exc())
            return {
                "error": f"Failed to process essay highlights: {e}",
                "highlighted_essay_html": essay,
                "highlights": {"green": [], "red": [], "yellow": []},
                "explanations": {"green": [], "red": [], "yellow": []}
            } 