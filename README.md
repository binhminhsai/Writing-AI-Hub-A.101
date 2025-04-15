# IELTS Writing AI

An AI-powered platform for IELTS Writing Task 2 practice and grading.

## Features

- **Question Generator**: Generate custom IELTS Writing Task 2 questions on any topic
- **Essay Grading**: Get detailed feedback and band scores for your essays
- **Sentence Analysis**: Highlight good, wrong, and improvable sentences with explanations

## Setup

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/project_workflow_ai.git
   cd project_workflow_ai
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - For real GPT responses: Create a `.env` file with your OpenAI API key:
     ```
     OPENAI_API_KEY=your-openai-api-key
     ```
   - For testing with mock responses: No API key needed

### Running the Application

#### Development Mode with Mock Responses

For UI testing without using the OpenAI API:

```
python run_dev.py
```

#### Production Mode with Real GPT Responses

```
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Usage

1. Open your browser and go to `http://localhost:8000`
2. Choose either "Practice Questions" or "Essay Grading"
3. For grading:
   - Select the question type
   - Enter the IELTS question
   - Paste your essay
   - Click "Grade Essay"

## Project Structure

```
project_workflow_ai/
├── workflows/
│   ├── workflow_1_question/    # Question generation workflow
│   └── workflow_2_grading/     # Essay grading workflow
├── shared/
│   ├── templates/              # Jinja2 templates
│   │   ├── base/               # Base layout templates
│   │   ├── prompt_writing/     # Writing prompts
│   │   └── prompt_grading/     # Grading prompts
│   └── utils/                  # Shared utilities
├── public/                     # Static files
│   ├── css/                    # Stylesheets
│   └── js/                     # JavaScript files
└── app.py                      # Main FastAPI application
```

## License

MIT

## Acknowledgements

- OpenAI for GPT models
- IELTS for band descriptors and criteria