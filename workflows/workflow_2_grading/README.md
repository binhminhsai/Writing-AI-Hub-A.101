# IELTS Writing Task 2 Grading Workflow

This workflow provides automated grading and analysis for IELTS Writing Task 2 essays using AI.

## Features

- **Comprehensive Analysis**: Essays are analyzed based on the four official IELTS Writing Task 2 criteria:
  - Task Response
  - Coherence and Cohesion
  - Lexical Resource
  - Grammatical Range and Accuracy

- **Detailed Feedback**: Provides detailed strengths and weaknesses for each criterion, with specific examples from the essay.

- **Band Scoring**: Calculates IELTS band scores for each criterion and overall average band.

- **Sentence-Level Analysis**: Highlights sentences as:
  - 🟢 Good (correct, strong, high band contribution)
  - 🔴 Wrong (grammatically incorrect or flawed)
  - 🟡 Improvable (vague, weak, or unclear)

- **Improvement Suggestions**: Provides corrected versions of problematic sentences and improvement suggestions.

## How It Works

1. The workflow uses an orchestration agent to coordinate multiple tools:
   - Tool 1: Analyzes the essay based on official IELTS criteria
   - Tool 2: Highlights and explains sentences

2. Each tool uses AI to process the essay and provide detailed feedback.

3. The results are combined into a comprehensive grading response.

## API

### Endpoint

```
POST /workflow_2_grading/analyze
```

### Request Format

```json
{
  "essay": "The essay text...",
  "question": "The IELTS Writing Task 2 question...",
  "types": "The question type (Opinion, Discussion, etc.)"
}
```

### Response Format

```json
{
  "feedback": {
    "Task Response": { ... },
    "Coherence and Cohesion": { ... },
    "Lexical Resource": { ... },
    "Grammatical Range and Accuracy": { ... }
  },
  "scores": {
    "task": 6.0,
    "coherence": 6.5,
    "lexical": 6.0,
    "grammar": 6.0
  },
  "average_band": 6.0,
  "essay_highlights": "<span style='...'>...</span>",
  "highlighted_sentences": {
    "green": [ ... ],
    "red": [ ... ],
    "yellow": [ ... ]
  },
  "explanations": {
    "green": [ ... ],
    "red": [ ... ],
    "yellow": [ ... ]
  }
}
```

## Frontend

The workflow includes a user-friendly frontend at `/workflow_2_grading/` that allows users to:

1. Enter an IELTS question and essay
2. Submit for grading
3. View detailed feedback and scores
4. See highlighted sentences with explanations

## Usage in Other Applications

The grading workflow can be integrated into other applications by making HTTP requests to the API endpoint.

```javascript
// Example fetch request
const response = await fetch('/workflow_2_grading/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    essay: "...",
    question: "...",
    types: "Opinion"
  })
});

const result = await response.json();
``` 