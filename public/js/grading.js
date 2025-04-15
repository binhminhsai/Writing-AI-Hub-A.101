/**
 * IELTS Writing Task 2 Grading Frontend Script
 */

document.addEventListener('DOMContentLoaded', function() {
    // Form and UI elements
    const gradingForm = document.getElementById('grading-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');
    
    // Score elements
    const taskScore = document.getElementById('task-score');
    const coherenceScore = document.getElementById('coherence-score');
    const lexicalScore = document.getElementById('lexical-score');
    const grammarScore = document.getElementById('grammar-score');
    const averageBand = document.getElementById('average-band');
    
    // Content sections
    const feedbackSection = document.getElementById('feedback-section');
    const highlightedEssay = document.getElementById('highlighted-essay');
    const explanationsSection = document.getElementById('explanations');
    
    // Form submission handler
    gradingForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Reset previous results
        resetUI();
        
        // Get form data
        const formData = new FormData(gradingForm);
        const requestData = {
            essay: formData.get('essay'),
            question: formData.get('question'),
            types: formData.get('types')
        };
        
        // Validate input
        if (!requestData.essay.trim() || !requestData.question.trim() || !requestData.types) {
            showError('Please fill out all fields.');
            return;
        }
        
        // Show loading state
        showLoading();
        
        try {
            // Send API request
            const response = await fetch('/workflow_2_grading/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            let responseData;
            
            try {
                // Try to parse as JSON, regardless of HTTP status
                responseData = await response.json();
            } catch (jsonError) {
                // If not valid JSON, get text and show error
                const textResponse = await response.text();
                console.error('Invalid JSON response:', textResponse);
                showError(`Server returned invalid response format: ${textResponse.substring(0, 100)}...`);
                return;
            }
            
            // Check for API errors that still return JSON
            if (!response.ok) {
                const errorMessage = responseData.error || responseData.detail || 'Failed to analyze essay';
                showError(errorMessage);
                console.error('API Error:', responseData);
                
                // If we have scores even with an error, still try to display them
                if (responseData.scores && responseData.feedback) {
                    displayResults(responseData);
                }
                return;
            }
            
            // Process valid response
            displayResults(responseData);
            
        } catch (error) {
            showError(error.message || 'Something went wrong.');
            console.error('Error:', error);
        } finally {
            hideLoading();
        }
    });
    
    /**
     * Display the grading results in the UI
     */
    function displayResults(data) {
        // Display scores
        taskScore.textContent = data.scores["Task Response"].toFixed(1);
        coherenceScore.textContent = data.scores["Coherence and Cohesion"].toFixed(1);
        lexicalScore.textContent = data.scores["Lexical Resource"].toFixed(1);
        grammarScore.textContent = data.scores["Grammatical Range and Accuracy"].toFixed(1);
        averageBand.textContent = data.average_band.toFixed(1);
        
        // Display feedback
        displayFeedback(data.feedback);
        
        // Display highlighted essay
        highlightedEssay.innerHTML = data.essay_highlights;
        
        // Display explanations
        displayExplanations(data.explanations);
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    /**
     * Display detailed feedback for each criterion
     */
    function displayFeedback(feedback) {
        feedbackSection.innerHTML = '<h2>Detailed Feedback</h2>';
        
        // Create sections for each criterion
        const criteria = [
            { key: 'Task Response', title: 'Task Response' },
            { key: 'Coherence and Cohesion', title: 'Coherence & Cohesion' },
            { key: 'Lexical Resource', title: 'Lexical Resource' },
            { key: 'Grammatical Range and Accuracy', title: 'Grammar & Accuracy' }
        ];
        
        criteria.forEach(criterion => {
            if (feedback[criterion.key]) {
                const criterionData = feedback[criterion.key];
                
                // Create criterion container
                const criterionElement = document.createElement('div');
                criterionElement.className = 'feedback-criteria';
                
                // Add title
                const titleElement = document.createElement('h3');
                titleElement.className = 'criteria-title';
                titleElement.textContent = criterion.title;
                criterionElement.appendChild(titleElement);
                
                // Add strengths
                if (criterionData.Strengths && criterionData.Strengths.length) {
                    const strengthsElement = document.createElement('div');
                    strengthsElement.innerHTML = `<h4>✅ Strengths</h4><ul>${criterionData.Strengths.map(strength => `<li>${strength}</li>`).join('')}</ul>`;
                    criterionElement.appendChild(strengthsElement);
                }
                
                // Add weaknesses
                if (criterionData.Weaknesses && criterionData.Weaknesses.length) {
                    const weaknessesElement = document.createElement('div');
                    weaknessesElement.innerHTML = `<h4>❌ Weaknesses</h4><ul>${criterionData.Weaknesses.map(weakness => `<li>${weakness}</li>`).join('')}</ul>`;
                    criterionElement.appendChild(weaknessesElement);
                }
                
                // Add justification
                let bandScore = null;
                if (criterionData['Band Score Justification']) {
                    const justificationText = criterionData['Band Score Justification'];
                    const justificationElement = document.createElement('div');
                    justificationElement.innerHTML = `<h4>Band Score Justification</h4><p>${justificationText}</p>`;
                    criterionElement.appendChild(justificationElement);

                    // Extract the score number for dynamic key lookup
                    const scoreMatch = justificationText.match(/Band\s+(\d+\.?\d*)/);
                    if (scoreMatch && scoreMatch[1]) {
                        bandScore = scoreMatch[1]; 
                        console.log(`[displayFeedback] Extracted band score: '${bandScore}' for ${criterion.key}`);
                    } else {
                        console.error(`[displayFeedback] Failed to extract band score from: ${justificationText}`);
                    }
                }

                // Log all available keys in the criterion data
                console.log(`[displayFeedback] Available keys for ${criterion.key}:`, Object.keys(criterionData));

                // Add 'Why not Band +0.5?' if it exists
                if (bandScore) {
                    const plusKey = `Why not Band ${bandScore} + 0.5?`;
                    console.log(`[displayFeedback] Checking for plus key: '${plusKey}'`);
                    
                    // Check both formats of the key
                    const higherScoreKey = Object.keys(criterionData).find(key => 
                        key.includes("Why didn't it score higher?") || 
                        key === plusKey
                    );
                    
                    if (criterionData[higherScoreKey]) {
                        console.log(`[displayFeedback] Found higher score content`);
                        const plusElement = document.createElement('div');
                        plusElement.innerHTML = `<h4>${plusKey}</h4><p>${criterionData[higherScoreKey]}</p>`;
                        criterionElement.appendChild(plusElement);
                    }
                }

                // Add 'Why not Band -0.5?' if it exists
                if (bandScore) {
                    const minusKey = `Why not Band ${bandScore} - 0.5?`;
                    console.log(`[displayFeedback] Checking for minus key: '${minusKey}'`);
                    
                    // Check both formats of the key
                    const lowerScoreKey = Object.keys(criterionData).find(key => 
                        key.includes("Why didn't it score lower?") ||
                        key === minusKey
                    );
                    
                    if (criterionData[lowerScoreKey]) {
                        console.log(`[displayFeedback] Found lower score content`);
                        const minusElement = document.createElement('div');
                        minusElement.innerHTML = `<h4>${minusKey}</h4><p>${criterionData[lowerScoreKey]}</p>`;
                        criterionElement.appendChild(minusElement);
                    }
                }
                
                // Add to feedback section
                feedbackSection.appendChild(criterionElement);
            }
        });
    }
    
    /**
     * Display sentence explanations
     */
    function displayExplanations(explanations) {
        explanationsSection.innerHTML = '<h2>Sentence Explanations</h2>';
        
        // Categories of explanations
        const categories = [
            { key: 'green', title: '🟢 Good Sentences', color: '#d4edda' },
            { key: 'red', title: '🔴 Wrong Sentences', color: '#f8d7da' },
            { key: 'yellow', title: '🟡 Improvable Sentences', color: '#fff3cd' }
        ];
        
        categories.forEach(category => {
            if (explanations[category.key] && explanations[category.key].length) {
                // Create category container
                const categoryElement = document.createElement('div');
                categoryElement.className = 'explanation-category';
                
                // Add title
                const titleElement = document.createElement('h3');
                titleElement.textContent = category.title;
                categoryElement.appendChild(titleElement);
                
                // Add explanation items
                explanations[category.key].forEach(item => {
                    const itemElement = document.createElement('div');
                    itemElement.className = 'explanation-item';
                    itemElement.style.borderLeft = `4px solid ${category.color}`;
                    
                    // Content depends on category
                    let content = '';
                    
                    if (category.key === 'green') {
                        content = `
                            <p><strong>Sentence:</strong> "${item.sentence}"</p>
                            <p><strong>Reason:</strong> ${item.reason}</p>
                        `;
                    } else if (category.key === 'red') {
                        content = `
                            <p><strong>Sentence:</strong> "${item.sentence}"</p>
                            <p><strong>Error:</strong> ${item.error}</p>
                            <p><strong>Correction:</strong> "${item.correction}"</p>
                            <p><strong>Reason:</strong> ${item.reason}</p>
                        `;
                    } else if (category.key === 'yellow') {
                        content = `
                            <p><strong>Sentence:</strong> "${item.sentence}"</p>
                            <p><strong>Issue:</strong> ${item.issue}</p>
                            <p><strong>Improved:</strong> "${item.improved}"</p>
                            <p><strong>Reason:</strong> ${item.reason}</p>
                        `;
                    }
                    
                    itemElement.innerHTML = content;
                    categoryElement.appendChild(itemElement);
                });
                
                // Add to explanations section
                explanationsSection.appendChild(categoryElement);
            }
        });
    }
    
    /**
     * Reset the UI state
     */
    function resetUI() {
        errorMessage.style.display = 'none';
        resultsSection.style.display = 'none';
        feedbackSection.innerHTML = '';
        highlightedEssay.innerHTML = '';
        explanationsSection.innerHTML = '';
    }
    
    /**
     * Show loading state
     */
    function showLoading() {
        submitBtn.disabled = true;
        loadingSection.style.display = 'block';
    }
    
    /**
     * Hide loading state
     */
    function hideLoading() {
        submitBtn.disabled = false;
        loadingSection.style.display = 'none';
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }
});