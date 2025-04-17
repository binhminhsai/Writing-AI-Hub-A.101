/**
 * IELTS Writing Task 2 Grading Frontend Script
 */

document.addEventListener('DOMContentLoaded', async function() {
    // Form and UI elements
    const gradingForm = document.getElementById('grading-form');
    const submitBtn = document.getElementById('submit-btn');
    const loadingSection = document.getElementById('loading');
    const resultsSection = document.getElementById('results');
    const errorMessage = document.getElementById('error-message');
    
    // Score elements
    const scoreItemTA = document.getElementById('score-item-ta');
    const scoreItemCC = document.getElementById('score-item-cc');
    const scoreItemLR = document.getElementById('score-item-lr');
    const scoreItemGRA = document.getElementById('score-item-gra');
    const overallScoreEl = document.getElementById('overall-score');
    
    // Stats elements
    const statWordCount = document.getElementById('stat-word-count');
    const statCompletionTime = document.getElementById('stat-completion-time');
    const statVocabRange = document.getElementById('stat-vocab-range');
    const statGrammarAccuracy = document.getElementById('stat-grammar-accuracy');

    // Feedback elements
    // const feedbackStrengthsList = document.querySelector('#feedback-strengths .feedback-list');
    // const feedbackImprovementsList = document.querySelector('#feedback-improvements .feedback-list');

    // Buttons
    const downloadBtn = document.getElementById('download-feedback');
    const tryAgainBtn = document.getElementById('try-again');
    
    // Reset UI initially
    resetUI();
    showLoading(); // Show loading immediately

    // --- Get DOM Elements --- 
    const loadingIndicator = document.getElementById('loading');
    const gradingLoadingText = document.getElementById('grading-loading-text');
    // const gradingProgressBar = document.getElementById('grading-progress-bar'); // REMOVED
    const criteriaTabButtonsContainer = document.getElementById('criteria-tab-buttons');
    const criteriaTabContentsContainer = document.getElementById('criteria-tab-contents');
    const highlightedEssayDiv = document.getElementById('highlighted-essay-html');
    const explanationsDiv = document.getElementById('explanations');

    let gradingLoadingInterval = null; // For text animation
    // let gradingProgressInterval = null; // REMOVED

    // --- Grading Animation Data & Functions ---
    const gradingMessages = [
        "Booting up the AI Grader... <i class=\"fas fa-robot\"></i>",
        "Reading the question and essay... <i class=\"fas fa-book-reader\"></i>",
        "Analyzing Task Achievement... <i class=\"fas fa-bullseye\"></i>",
        "Evaluating Coherence & Cohesion... <i class=\"fas fa-link\"></i>",
        "Assessing Lexical Resource richness... <i class=\"fas fa-spell-check\"></i>", // Using spell-check icon for vocab
        "Checking Grammar & Accuracy... <i class=\"fas fa-check-double\"></i>",
        "Calculating Scores... <i class=\"fas fa-calculator\"></i>",
        "Identifying Strengths... <i class=\"fas fa-thumbs-up\"></i>",
        "Pinpointing Areas for Improvement... <i class=\"fas fa-search\"></i>",
        "Highlighting key text sections... <i class=\"fas fa-highlighter\"></i>",
        "Generating helpful explanations... <i class=\"fas fa-comment-dots\"></i>",
        "Compiling the final assessment... <i class=\"fas fa-file-signature\"></i>",
        "Just a moment more... Polishing the report! ✨"
    ];
    let currentGradingMsgIndex = 0;

    function startGradingAnimation() {
        console.log("[DEBUG] StartGradingAnimation called."); 
        currentGradingMsgIndex = 0;
        if (gradingLoadingText) {
             gradingLoadingText.innerHTML = `${gradingMessages[0]} <i class="fas fa-spinner fa-spin"></i>`; // Start with first message + spinner
        }
        // if (gradingProgressBar) gradingProgressBar.style.width = '0%'; // REMOVED
        if (loadingIndicator) loadingIndicator.style.display = 'flex';
        if (resultsSection) resultsSection.style.display = 'none';
        if (errorMessage) errorMessage.style.display = 'none';

        // Clear previous text interval
        if (gradingLoadingInterval) clearInterval(gradingLoadingInterval);
        // if (gradingProgressInterval) clearInterval(gradingProgressInterval); // REMOVED

        // Start Text Interval
        gradingLoadingInterval = setInterval(() => {
            currentGradingMsgIndex = (currentGradingMsgIndex + 1) % gradingMessages.length;
            if (gradingLoadingText) { 
                 gradingLoadingText.innerHTML = `${gradingMessages[currentGradingMsgIndex]} <i class="fas fa-spinner fa-spin"></i>`;
            }
        }, 3000); // Keep 3 second interval

        // REMOVED Progress Bar Interval Logic
        
        console.log("[DEBUG] Started Grading Animation (Text Only).");
    }

    function stopGradingAnimation() {
        console.log("[DEBUG] Stopping Grading Animation.");
        if (loadingIndicator) loadingIndicator.style.display = 'none';
        if (gradingLoadingInterval) clearInterval(gradingLoadingInterval);
        // if (gradingProgressInterval) clearInterval(gradingProgressInterval); // REMOVED
        gradingLoadingInterval = null;
        // gradingProgressInterval = null; // REMOVED
    }
    // --- End Grading Animation --- 

    // --- Data Fetching from LocalStorage --- 
    console.log("[DEBUG] Attempting to read 'gradingTaskData' from localStorage...");
    const gradingTaskDataStr = localStorage.getItem('gradingTaskData');
    console.log(`[DEBUG] Value read from localStorage for 'gradingTaskData':`, gradingTaskDataStr ? gradingTaskDataStr.substring(0, 200) + '...' : '(null or empty)'); // Log the value read

    if (!gradingTaskDataStr) {
        console.error("[DEBUG] 'gradingTaskData' not found or empty. Cannot proceed."); // More specific log
        showError('Required grading data not found. Please start from the practice page.');
        hideLoading();
        return;
    }

    let gradingTaskData;
    try {
        gradingTaskData = JSON.parse(gradingTaskDataStr);
        // Remove the data from localStorage now that we've loaded it?
        // localStorage.removeItem('gradingTaskData'); 
    } catch (e) {
        showError('Error parsing grading data. Please try again.');
        console.error("Error parsing localStorage:", e);
        hideLoading();
        return;
    }

    // --- Prepare API Request (use data from the new object) --- 
        const requestData = {
        essay: gradingTaskData.essay,
        question: gradingTaskData.question, 
        types: gradingTaskData.task_type || 'TASK2' // Default if missing
    };

    // Check specifically for the required fields within the loaded object
    if (!requestData.essay || !requestData.question || !requestData.types) {
         showError('Missing critical data (essay, question, or type) within the session. Please try again.');
         console.error("Missing fields in gradingTaskData:", gradingTaskData);
         hideLoading();
            return;
        }
        
    // Call Grading API
        try {
        console.log("Sending grading request:", requestData);
            const response = await fetch('/workflow_2_grading/analyze', {
                method: 'POST',
            headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });
            
            let responseData;
            try {
                responseData = await response.json();
            console.log("Received grading response:", responseData);
            } catch (jsonError) {
                const textResponse = await response.text();
            console.error('Invalid JSON response from grading API:', textResponse);
                showError(`Server returned invalid response format: ${textResponse.substring(0, 100)}...`);
            return; // Exit after showing error
            }
            
            if (!response.ok) {
            const errorMsg = responseData.error || responseData.detail || 'Failed to analyze essay';
            showError(errorMsg);
            console.error('Grading API Error:', responseData);
            // Optionally display partial results if available?
            // if (responseData.scores && responseData.feedback) displayResults(responseData, gradingTaskData);
            return; // Exit after showing error
        }

        // Process & Display Valid Response
        displayResults(responseData, gradingTaskData); 
            
        } catch (error) {
        showError(error.message || 'Something went wrong during grading.');
        console.error('Grading Fetch Error:', error);
        } finally {
        stopGradingAnimation(); // <<< USE NEW ANIMATION STOP
        }
    
    /**
     * Display the grading results in the UI
     */
    function displayResults(apiResponseData, taskData) {
        // Scores & Bars
        updateScoreItem(scoreItemTA, apiResponseData.scores?.['Task Response'] || 0);
        updateScoreItem(scoreItemCC, apiResponseData.scores?.['Coherence and Cohesion'] || 0);
        updateScoreItem(scoreItemLR, apiResponseData.scores?.['Lexical Resource'] || 0);
        updateScoreItem(scoreItemGRA, apiResponseData.scores?.['Grammatical Range and Accuracy'] || 0);
        overallScoreEl.textContent = (apiResponseData.average_band || 0).toFixed(1);

        // Stats
        statWordCount.textContent = taskData.essay?.match(/\b\w+\b/g)?.length || 0;
        
        // <<< Calculate Completion Time >>>
        const timeLimitSeconds = (taskData.timeLimit || 0) * 60;
        const timeLeftSeconds = taskData.timeLeft !== undefined ? taskData.timeLeft : timeLimitSeconds; // Use timeLeft if available, else assume full time used
        const completionSeconds = Math.max(0, timeLimitSeconds - timeLeftSeconds); // Ensure non-negative
        statCompletionTime.textContent = formatTimeMMSS(completionSeconds); 
        
        // <<< Vocab/Grammar Levels >>>
        const vocabScore = apiResponseData.scores?.['Lexical Resource'] || 0;
        const grammarScore = apiResponseData.scores?.['Grammatical Range and Accuracy'] || 0;
        statVocabRange.textContent = mapScoreToLevelDescription(vocabScore);
        statGrammarAccuracy.textContent = mapScoreToLevelDescription(grammarScore);

        // Populate Criteria Feedback Tabs
        populateCriteriaTabs(criteriaTabButtonsContainer, criteriaTabContentsContainer, apiResponseData.feedback);
        
        // Populate Highlighted Essay 
        if (highlightedEssayDiv && apiResponseData.essay_highlights) {
             highlightedEssayDiv.innerHTML = apiResponseData.essay_highlights; 
        } else if (highlightedEssayDiv) {
            highlightedEssayDiv.innerHTML = '<p><i>Highlighted essay not available.</i></p>';
        }
        
        // Populate Explanations (Filtered)
        populateExplanations(explanationsDiv, apiResponseData.explanations);
        
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    function updateScoreItem(element, score) {
        const valueElement = element?.querySelector('.score-value');
        const fillElement = element?.querySelector('.score-fill');
        if (valueElement) valueElement.textContent = score.toFixed(1);
        if (fillElement) {
            const percentage = Math.max(0, Math.min(100, (score / 9.0) * 100));
            fillElement.style.width = `${percentage}%`;
        }
    }

    function formatTimeMMSS(totalSeconds) {
        if (totalSeconds <= 0) return '--:--';
        const minutes = Math.floor(totalSeconds / 60);
        const seconds = totalSeconds % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    /**
     * Reset the UI state
     */
    function resetUI() {
        errorMessage.style.display = 'none';
        resultsSection.style.display = 'none';
        // Reset score displays if needed
        overallScoreEl.textContent = '-';
        // ... reset other score/stat elements ...
    }
    
    /**
     * Show loading state
     */
    function showLoading() {
        loadingSection.style.display = 'block';
        resultsSection.style.display = 'none'; 
        errorMessage.style.display = 'none'; 
    }
    
    /**
     * Hide loading state
     */
    function hideLoading() {
        loadingSection.style.display = 'none';
    }
    
    /**
     * Show error message
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        stopGradingAnimation(); // Stop animation on error
    }

    // <<< NEW: Function to populate detailed criteria feedback as TABS >>>
    function populateCriteriaTabs(buttonsContainer, contentsContainer, feedback) {
         if (!buttonsContainer || !contentsContainer || !feedback) {
              console.error("Missing elements or feedback data for criteria tabs.");
              return;
         }
         buttonsContainer.innerHTML = ''; // Clear old buttons
         contentsContainer.innerHTML = ''; // Clear old content
         
         const criteriaOrder = [
             { key: 'Task Response', title: 'Task Response' },
             { key: 'Coherence and Cohesion', title: 'Coherence & Cohesion' },
             { key: 'Lexical Resource', title: 'Lexical Resource' },
             { key: 'Grammatical Range and Accuracy', title: 'Grammar & Accuracy' }
         ];

         criteriaOrder.forEach((criterion, index) => {
             const criterionData = feedback[criterion.key];
             if (!criterionData) return; // Skip if no data for this criterion

             const tabId = `criteria-tab-${index}`;

             // Create Button
             const button = document.createElement('button');
             button.className = 'criteria-tab-button';
             button.textContent = criterion.title;
             button.dataset.target = tabId;
             if (index === 0) button.classList.add('active'); 
             buttonsContainer.appendChild(button);

             // Create Content Div
             const contentDiv = document.createElement('div');
             contentDiv.className = 'criteria-tab-content';
             contentDiv.id = tabId;
             if (index === 0) contentDiv.classList.add('active');

             // --- Populate Content Div --- 
             let contentHtml = '';

             // Strengths
             if (criterionData.Strengths && criterionData.Strengths.length > 0) {
                 contentHtml += `<h4><i class="fas fa-check-circle" style="color: #10b981;"></i> Strengths</h4><ul class="feedback-list">`;
                 criterionData.Strengths.forEach(item => { contentHtml += `<li>${item}</li>`; });
                 contentHtml += `</ul>`;
             } else {
                  contentHtml += `<h4><i class="fas fa-check-circle" style="color: #10b981;"></i> Strengths</h4><p><i>None specified.</i></p>`;
             }
             
             // Weaknesses (Areas for Improvement)
             if (criterionData.Weaknesses && criterionData.Weaknesses.length > 0) {
                 contentHtml += `<h4 style="margin-top: 1rem;"><i class="fas fa-exclamation-circle" style="color: #f59e0b;"></i> Areas for Improvement</h4><ul class="feedback-list">`;
                 criterionData.Weaknesses.forEach(item => { contentHtml += `<li>${item}</li>`; });
                 contentHtml += `</ul>`;
              } else {
                   contentHtml += `<h4 style="margin-top: 1rem;"><i class="fas fa-exclamation-circle" style="color: #f59e0b;"></i> Areas for Improvement</h4><p><i>None specified.</i></p>`;
              }
             
             // Helper to add justification paragraph
             const addJustificationPara = (label, dataKey) => {
                 if (criterionData[dataKey]) {
                     contentHtml += `<p style="margin-top: 1rem;"><strong style="color:var(--muted);">${label}:</strong> ${criterionData[dataKey]}</p>`;
                 }
             };

             addJustificationPara('Band Score Justification', 'Band Score Justification');
             
             // Find and add 'Why not higher/lower'
             const keys = Object.keys(criterionData);
             const whyHigherKey = keys.find(k => k.toLowerCase().includes("why not band") && k.includes("+"));
             const whyLowerKey = keys.find(k => k.toLowerCase().includes("why not band") && (k.includes("-") || k.includes("–"))); 
             
             if(whyHigherKey) addJustificationPara(whyHigherKey, whyHigherKey);
             if(whyLowerKey) addJustificationPara(whyLowerKey, whyLowerKey);
             // --- End Populate Content Div --- 

             contentDiv.innerHTML = contentHtml;
             contentsContainer.appendChild(contentDiv);
         });

         // Add event listeners AFTER all buttons/content are added
         const newCritButtons = buttonsContainer.querySelectorAll('.criteria-tab-button');
         const newCritContents = contentsContainer.querySelectorAll('.criteria-tab-content');
         newCritButtons.forEach(button => {
             button.addEventListener('click', () => {
                 newCritButtons.forEach(btn => btn.classList.remove('active'));
                 newCritContents.forEach(content => content.classList.remove('active'));
                 button.classList.add('active');
                 const targetContent = document.getElementById(button.dataset.target);
                 if (targetContent) targetContent.classList.add('active');
             });
         });
    }
    
    // <<< Keep MODIFIED: Function to populate explanations >>>
    function populateExplanations(container, explanations) {
        if (!container || !explanations) {
             if(container) container.innerHTML = '<p>Sentence explanations not available.</p>';
             return;
        }
        container.innerHTML = '<h2>Sentence Explanations</h2>'; 
        
        // <<< Filter categories: Only Red and Yellow >>>
        const categories = [
            // { key: 'green', title: '🟢 Good Examples', color: '#10b981' }, // REMOVED GREEN
            { key: 'red', title: '🔴 Errors & Corrections', color: '#ef4444' },
            { key: 'yellow', title: '🟡 Suggestions for Improvement', color: '#f59e0b' }
        ];

        let contentAdded = false;
        categories.forEach(category => {
            const items = explanations[category.key];
            if (items && items.length > 0) {
                contentAdded = true;
                const categoryDiv = document.createElement('div');
                categoryDiv.style.marginBottom = '1.5rem';

                const titleEl = document.createElement('h4');
                titleEl.textContent = category.title;
                titleEl.style.color = category.color; 
                titleEl.style.fontWeight = '600';
                titleEl.style.marginBottom = '0.75rem';
                categoryDiv.appendChild(titleEl);

                items.forEach(item => {
                    const itemDiv = document.createElement('div');
                    itemDiv.style.borderLeft = `3px solid ${category.color}`;
                    itemDiv.style.paddingLeft = '1rem';
                    itemDiv.style.marginBottom = '1rem';
                    itemDiv.style.fontSize = '0.9em'; 
                    
                    let itemHtml = '';
                    // Keep logic for displaying different detail types
                    if(item.sentence) itemHtml += `<p><em>Original:</em> "${item.sentence}"</p>`;
                    if(item.error) itemHtml += `<p><strong>Error:</strong> ${item.error}</p>`;
                    if(item.correction) itemHtml += `<p><strong>Correction:</strong> "${item.correction}"</p>`;
                    if(item.issue) itemHtml += `<p><strong>Issue:</strong> ${item.issue}</p>`;
                    if(item.improved) itemHtml += `<p><strong>Improved:</strong> "${item.improved}"</p>`;
                    if(item.reason) itemHtml += `<p><strong>Reason:</strong> ${item.reason}</p>`;
                    
                    itemDiv.innerHTML = itemHtml;
                    categoryDiv.appendChild(itemDiv);
                });
                container.appendChild(categoryDiv);
            }
        });

        if (!contentAdded) {
             // Update fallback message
             container.innerHTML += '<p>No specific errors or suggestions provided for sentences.</p>'; 
        }
    }

    // --- Button Actions --- 
    if(downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            // Basic print functionality for download
             alert('Printing feedback... Please use your browser print options (e.g., Save as PDF).');
             window.print(); 
        });
    }
    if(tryAgainBtn) {
        tryAgainBtn.addEventListener('click', () => {
            // Go back to practice settings page
             window.location.href = '/setting.html'; 
        });
    }

    // <<< NEW: Helper to map IELTS score to CEFR-like description >>>
    function mapScoreToLevelDescription(score) {
        score = parseFloat(score) || 0;
        if (score >= 8.0) return "Proficient (C2 Level)";
        if (score >= 7.0) return "Advanced (C1 Level)"; // 7.0 - 7.5
        if (score >= 5.5) return "Intermediate (B2 Level)"; // 5.5 - 6.5
        if (score >= 4.0) return "Developing (B1 Level)"; // 4.0 - 5.0
        return "Basic (A1/A2 Level)"; // Below 4.0
    }
});