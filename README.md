# YouBot — RAG-Powered YouTube Video Chat Extension

YouBot is an AI-powered Chrome extension that lets users ask natural-language questions about the YouTube video they are currently watching and receive context-aware answers grounded in the video's transcript.

Instead of manually searching through long videos, users can ask questions directly from the extension popup. YouBot processes the video transcript through a Retrieval-Augmented Generation (RAG) pipeline and uses Google Gemini to generate relevant, context-aware responses.

## Features

* Chat with the currently playing YouTube video
* Automatically detects the active YouTube video
* Extracts and processes video transcript content
* Supports natural-language questions
* RAG-based retrieval for relevant transcript context
* LangChain-powered document processing pipeline
* Gemini-powered response generation
* FastAPI backend for AI and retrieval workflows
* Lightweight Chrome extension interface
* Loading states and error handling
* Context-grounded answers based on video content

## Tech Stack

| Category          | Technologies                                |
| ----------------- | ------------------------------------------- |
| Browser Extension | JavaScript, HTML, CSS, Chrome Extension API |
| Backend           | Python, FastAPI                             |
| AI Framework      | LangChain                                   |
| AI Model          | Google Gemini API                           |
| Architecture      | Retrieval-Augmented Generation (RAG)        |
| Data Source       | YouTube Video Transcripts                   |
| Communication     | REST APIs, Asynchronous Fetch               |

## How It Works

```text
YouTube Video
      |
      v
Chrome Extension
      |
      | Detect Current Video
      v
Extract Video ID
      |
      v
FastAPI Backend
      |
      v
Fetch Video Transcript
      |
      v
Transcript Processing
      |
      v
Text Chunking with LangChain
      |
      v
Relevant Context Retrieval
      |
      v
User Question + Retrieved Context
      |
      v
Gemini API
      |
      v
Context-Aware Answer
      |
      v
Chrome Extension Popup
```

## RAG Pipeline

YouBot uses a Retrieval-Augmented Generation pipeline to improve the relevance of generated answers.

The workflow consists of:

1. Retrieve the transcript of the active YouTube video.
2. Process and split the transcript into smaller chunks.
3. Use LangChain to manage the document-processing and retrieval workflow.
4. Identify transcript context relevant to the user's question.
5. Send the retrieved context together with the question to Gemini.
6. Return the generated answer to the Chrome extension popup.

This approach helps ground responses in the actual content of the video rather than relying only on the model's general knowledge.

## Project Structure

```text
You_bot/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   └── ...
│
├── extension/
│   ├── manifest.json
│   ├── popup.html
│   ├── popup.css
│   ├── popup.js
│   └── icons/
│
├── .gitignore
└── README.md
```

> The exact folder structure may vary depending on your local setup.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/itzmit49/You_bot.git
cd You_bot
```

### 2. Set Up the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the backend directory:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit your `.env` file or API keys to GitHub.

Add environment files to `.gitignore`:

```gitignore
.env
.env.*
!.env.example
backend/.env
```

You can also create a safe `.env.example` file:

```env
GEMINI_API_KEY=your_api_key_here
```

### 4. Start the FastAPI Backend

Run the backend server:

```bash
uvicorn main:app --reload
```

The backend should now run locally, typically at:

```text
http://127.0.0.1:8000
```

### 5. Load the Chrome Extension

1. Open Google Chrome.
2. Go to `chrome://extensions/`.
3. Enable **Developer mode**.
4. Click **Load unpacked**.
5. Select the folder containing `manifest.json`.
6. Pin YouBot from the Chrome extensions menu.

### 6. Use YouBot

1. Open a YouTube video with an available transcript.
2. Click the YouBot extension icon.
3. Enter a question about the video.
4. Submit the question.
5. Receive an AI-generated response grounded in the video transcript.

Example questions:

```text
What is the main topic of this video?
```

```text
Explain the concept discussed at the beginning.
```

```text
What are the key points mentioned in the video?
```

```text
Summarize the explanation of machine learning.
```

## API Flow

The Chrome extension communicates asynchronously with the FastAPI backend.

Example request:

```json
{
  "video_id": "VIDEO_ID",
  "question": "What are the key concepts explained in this video?"
}
```

Example response:

```json
{
  "answer": "The video primarily explains..."
}
```

## Security

API keys must never be stored directly inside:

* `popup.js`
* `manifest.json`
* frontend JavaScript files
* committed `.env` files

All Gemini API requests should be handled through the backend.

If an API key has accidentally been committed to Git history, revoke or rotate it immediately before continuing development.

## Current Status

YouBot is currently available as a source-code project and can be run locally using Chrome's **Load unpacked** extension mode together with the FastAPI backend.

The extension is not currently published on the Chrome Web Store.

## Future Improvements

* Publish the extension on the Chrome Web Store
* Deploy the FastAPI backend
* Add conversational memory for follow-up questions
* Add source timestamps for retrieved transcript sections
* Support multilingual transcripts
* Add video summarization
* Improve retrieval quality for long videos
* Add streaming AI responses
* Cache processed transcripts
* Add support for transcript search and navigation
* Improve popup accessibility and keyboard navigation

## Author

**Harshit Kumar Vaibhav**

B.Tech in Computer Science and Engineering
National Institute of Technology Jalandhar


* LinkedIn: `https://github.com/summu2801/YouTube-bot`

## Repository

`https://github.com/summu2801/YouTube-bot`

## License

This project is intended for educational and development purposes.

---

If you find this project useful, consider giving the repository a star.
