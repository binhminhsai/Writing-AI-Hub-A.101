from typing import Dict
import asyncio
import json
import os
import traceback
from shared.services.gpt_prompt import render_template, send_prompt

async def generate_question_components(topic: str, band: str, task_type: str = "TASK2") -> Dict:
    """
    Generate IELTS Writing question and related components
    
    Args:
        topic: The topic for the question
        band: The target band score (e.g., "7.5")
        task_type: The task type (TASK1 or TASK2)
        
    Returns:
        Dictionary with generated components
    """
    try:
        print(f"\n[Question Generator] Starting with topic={topic}, band={band}, task_type={task_type}")
        print(f"[Question Generator] OPENAI_API_KEY present: {bool(os.environ.get('OPENAI_API_KEY'))}")
        
        # Default to Task 2 if not specified
        is_task1 = task_type == "TASK1"
        task_name = "Writing Task 1" if is_task1 else "Writing Task 2"
        print(f"[Question Generator] Task identified as {task_name}")
        
        # Step 1: Generate the question using question template
        try:
            print("[Question Generator] Preparing question prompt...")
            template_name = "prompt_writing/prompt_question.txt"
            question_prompt = render_template(template_name, 
                                  topic=topic, 
                                  band=band)
            print(f"[Question Generator] Question template rendered, length: {len(question_prompt)} chars")
        except Exception as e:
            print(f"[Question Generator] Error rendering question template: {e}")
            print(traceback.format_exc())
            return {
                "status": "error",
                "error": f"Question template error: {str(e)}",
                "traceback": traceback.format_exc()
            }
        
        # Send question prompt to GPT
        try:
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
                return {
                    "status": "error",
                    "error": question_data["error"],
                    "details": question_data.get("details", "")
                }
                
            # Extract the question 
            question_text = question_data.get("question", "")
            if not question_text:
                return {
                    "status": "error",
                    "error": "No question was generated from the API"
                }
                
            print(f"[Question Generator] Question generated: {question_text[:50]}...")
            
            # Step 2: Generate the outline based on the question
            print("[Question Generator] Preparing outline prompt...")
            outline_template = "prompt_writing/prompt_outline.txt"
            outline_prompt = render_template(outline_template,
                                       question=question_text,
                                       band=band)
            
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
                                     topic=topic,
                                     band=band)
            
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
                                        topic=topic,
                                        band=band)
            
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
                "question": question_text,
                "outline": outline_response,
                "vocabulary_suggestions": vocab_response,
                "sentence_suggestions": sentence_response,
                "topic": topic,
                "band": band,
                "task_type": task_name
            }
            
            print("[Question Generator] Successfully generated all components")
            return result
            
        except json.JSONDecodeError as e:
            print(f"[Question Generator] Failed to parse JSON: {e}")
            return {
                "status": "error",
                "error": f"Invalid JSON in API response: {str(e)}",
                "raw_response": question_response
            }
            
        except Exception as api_error:
            print(f"[Question Generator] API call error: {api_error}")
            return {
                "status": "error",
                "error": f"API call failed: {str(api_error)}",
                "traceback": traceback.format_exc()
            }
            
    except Exception as e:
        print(f"[Question Generator] Unexpected error: {e}")
        print(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }