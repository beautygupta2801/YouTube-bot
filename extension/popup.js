document.addEventListener("DOMContentLoaded", () => {
    const statusEl = document.getElementById("status");
    const mainUiEl = document.getElementById("main-ui");
    const videoIdDisplay = document.getElementById("video-id-display");
    const questionInput = document.getElementById("question-input");
    const askBtn = document.getElementById("ask-btn");
    const loadingEl = document.getElementById("loading");
    const responseArea = document.getElementById("response-area");

    let currentVideoId = null;

    // Detect if we are on a YouTube video page and extract ID
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || tabs.length === 0) return;
        const tab = tabs[0];
        
        if (tab.url && tab.url.includes("youtube.com/watch")) {
            // Ask content script for the video ID (or parse URL directly as fallback)
            chrome.tabs.sendMessage(tab.id, { action: "getVideoId" }, (response) => {
                if (chrome.runtime.lastError || !response) {
                    // Fallback to parsing URL if content script isn't ready
                    const url = new URL(tab.url);
                    currentVideoId = url.searchParams.get("v");
                } else if (response.videoId) {
                    currentVideoId = response.videoId;
                }

                if (currentVideoId) {
                    statusEl.style.display = "none";
                    mainUiEl.style.display = "block";
                    videoIdDisplay.textContent = currentVideoId;
                } else {
                    statusEl.textContent = "Could not detect video ID from this page.";
                }
            });
        } else {
            statusEl.textContent = "Please open a YouTube video to use this extension.";
        }
    });

    // Handle "Ask" button click
    askBtn.addEventListener("click", async () => {
        const question = questionInput.value.trim();
        if (!question) {
            showResponse("Please enter a question.", true);
            return;
        }

        // UI changes while loading
        askBtn.disabled = true;
        loadingEl.style.display = "block";
        responseArea.style.display = "none";
        responseArea.textContent = "";
        responseArea.classList.remove("error-text");

        try {
            // Send request to backend API
            // Important: Replace this URL with your actual backend endpoint if different
            const apiUrl = "http://127.0.0.1:8000/api/ask"; 
            
            const response = await fetch(apiUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    video_id: currentVideoId,
                    question: question
                })
            });

            if (!response.ok) {
                // Try to get the detailed error message from the backend
                let errorMessage = `Server error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    if (errorData && errorData.detail) {
                        errorMessage += ` - ${errorData.detail}`;
                    }
                } catch (e) {
                    // Ignore JSON parsing error
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            
            // Extract the answer. Adjust 'data.answer' depending on your backend's JSON structure
            const answerText = data.answer || data.response || data.message || JSON.stringify(data);
            showResponse(answerText, false);
            
        } catch (error) {
            showResponse(`Error: ${error.message}. Is your backend running?`, true);
        } finally {
            // Revert UI changes
            askBtn.disabled = false;
            loadingEl.style.display = "none";
        }
    });

    function showResponse(text, isError) {
        responseArea.style.display = "block";
        responseArea.textContent = text;
        if (isError) {
            responseArea.classList.add("error-text");
        } else {
            responseArea.classList.remove("error-text");
        }
    }
});
