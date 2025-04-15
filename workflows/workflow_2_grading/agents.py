import json
from typing import Dict, Any

from .constants import (
    PROMPT_AGENT,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    read_prompt
)
from .tools import Tool1AnalyzeAndScore, Tool2HighlightEssay

# Import send_prompt function from the merged module
from shared.services.gpt_prompt import send_prompt


class GradingAgent:
    """Orchestration agent for IELTS essay grading that coordinates multiple tools"""
    
    def __init__(self, model="gpt-4o-mini", temperature=0.2):
        self.model = model
        self.temperature = temperature
        self.agent_prompt_template = read_prompt(PROMPT_AGENT)
        
        # Initialize tools
        self.tool1 = Tool1AnalyzeAndScore(model, temperature)
        self.tool2 = Tool2HighlightEssay(model, temperature)
    
    async def run(self, question: str, essay: str, types: str) -> Dict[str, Any]:
        """Run the entire grading workflow"""
        
        try:
            # Sequential execution of tools
            
            # 1. Run Tool1: Analyze and Score
            tool1_result = await self.tool1.run(question, essay, types)
            
            # 2. Run Tool2: Highlight Essay
            tool2_result = await self.tool2.run(essay)
            
            # 3. Combine results
            result = {
                "feedback": tool1_result.get("feedback", {}),
                "scores": tool1_result.get("scores", {
                    "Task Response": 0,
                    "Coherence and Cohesion": 0,
                    "Lexical Resource": 0,
                    "Grammatical Range and Accuracy": 0
                }),
                "average_band": tool1_result.get("average_band", 0),
                "essay_highlights": tool2_result.get("highlighted_essay_html", essay),
                "highlighted_sentences": tool2_result.get("highlights", {"green": [], "red": [], "yellow": []}),
                "explanations": tool2_result.get("explanations", {"green": [], "red": [], "yellow": []})
            }
            
            return result
            
        except Exception as e:
            import traceback
            print(f"Error in grading agent execution: {str(e)}")
            print(traceback.format_exc())
            
            # Return error details for debugging
            return {
                "error": f"Failed to execute grading workflow: {str(e)}",
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
    
    async def run_with_agent(self, question: str, essay: str, types: str) -> Dict[str, Any]:
        """
        Alternative method that uses the agent prompt to coordinate tools
        via GPT rather than direct sequential execution
        """
        
        # Prepare agent prompt with parameters
        agent_prompt = self.agent_prompt_template.replace(
            "{{ question }}", question
        ).replace(
            "{{ essay }}", essay
        ).replace(
            "{{ types }}", types
        )
        
        # Define tools available to the agent
        tools = {
            "Tool1_AnalyzeAndScore": self.tool1.run,
            "Tool2_HighlightEssay": self.tool2.run
        }
        
        # Execute orchestration through GPT
        # This is an alternative approach, but for the current workflow,
        # the sequential direct execution in 'run' is more reliable and efficient
        
        try:
            # For simplicity, we'll use the direct sequential execution approach
            # This function is a placeholder for a more sophisticated agent-based approach
            return await self.run(question, essay, types)
            
        except Exception as e:
            print(f"Error in agent execution: {str(e)}")
            return {
                "error": "Failed to execute grading workflow",
                "details": str(e)
            }