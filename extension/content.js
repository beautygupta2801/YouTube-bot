// Minimal content script to detect YouTube and provide video ID if requested
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "getVideoId") {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const videoId = urlParams.get('v');
            sendResponse({ videoId: videoId });
        } catch (error) {
            sendResponse({ videoId: null });
        }
    }
    // Return true to indicate we will respond asynchronously if needed (though we respond synchronously here)
    return true; 
});
