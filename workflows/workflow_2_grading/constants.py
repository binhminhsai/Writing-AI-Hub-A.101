import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "shared" / "templates"
PROMPT_DIR = TEMPLATES_DIR / "prompt_grading"
SAMPLE_DIR = PROMPT_DIR / "samples"
ACCESS_SAMPLE_DIR = PROJECT_ROOT / "access" / "prompt_grading" / "sample"

# Prompt file paths
PROMPT_AGENT = PROMPT_DIR / "prompt_aigent.txt"
PROMPT_ANALYZE = PROMPT_DIR / "prompt_analyze.txt"
PROMPT_HIGHLIGHT = PROMPT_DIR / "prompt_highlight.txt"
PROMPT_SCORE = PROMPT_DIR / "prompt_score.txt"
BAND_DESCRIPTORS = SAMPLE_DIR / "band_descriptors.txt"
BAND_DESCRIPTORS_MEMORY = ACCESS_SAMPLE_DIR / "ielts_band_descriptors_memory.md"

# Default model settings
DEFAULT_MODEL = "gpt-4o-mini"  # Using GPT-4o mini for speed and potential better structure adherence
DEFAULT_TEMPERATURE = 0.2  # Low temperature for more consistent results

# Function to read a prompt template
def read_prompt(prompt_path):
    """Read a prompt template from file"""
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

# Load band descriptors
def get_band_descriptors():
    """Get IELTS band descriptors from file"""
    with open(BAND_DESCRIPTORS, "r", encoding="utf-8") as f:
        return f.read()

# Load enhanced band descriptors from memory
def get_band_descriptors_memory():
    """Get enhanced IELTS band descriptors from memory file"""
    try:
        with open(BAND_DESCRIPTORS_MEMORY, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Band descriptors memory file not found at {BAND_DESCRIPTORS_MEMORY}")
        return get_band_descriptors()  # Fall back to regular descriptors 