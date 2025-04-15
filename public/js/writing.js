document.getElementById('questionForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    const topic = document.getElementById('topic').value;
    const band = document.getElementById('band').value;
    const resultBox = document.getElementById('result');
    resultBox.textContent = 'Generating...';
  
    try {
        const response = await fetch('/api/workflow_1_question/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, band })
        });
        
        const data = await response.json();
        
        // Format the response nicely
        const formattedResult = `
TOPIC: ${data.topic}
BAND: ${data.band}

QUESTION:
${data.question}

OUTLINE:
${data.outline}

VOCABULARY:
${data.vocab}

SENTENCE STRUCTURES:
${data.sentence}
        `;
        
        resultBox.textContent = formattedResult;
    } catch (error) {
        resultBox.textContent = `Error: ${error.message}\nPlease try again.`;
    }
});
