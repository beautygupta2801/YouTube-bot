# YouBot — Chat with Any YouTube Video

YouBot is a Chrome extension that lets you ask questions about a YouTube video you're watching and get answers based on the video's actual transcript — not the AI's general knowledge.

You open a video, click the extension, ask a question like "what is this video about?", and get an answer grounded in what was actually said.

## How It Works

```text
YouTube Video
      |
      v
Chrome Extension (detects the video you're watching)
      |
      v
FastAPI Backend
      |
      v
Fetch video transcript (captions)
      |
      v
Split transcript into chunks
      |
      v
Convert chunks into embeddings (local, free — HuggingFace)
      |
      v
Find the chunks relevant to your question (FAISS search)
      |
      v
Send question + relevant chunks to an LLM (OpenRouter)
      |
      v
Answer sent back to the extension popup
```

This is a **Retrieval-Augmented Generation (RAG)** pipeline: instead of asking the AI to answer from memory, it retrieves the actual relevant parts of the transcript first, then asks the AI to answer using only that text.

## Tech Stack

| Category | Technology |
|---|---|
| Browser Extension | JavaScript, HTML, CSS, Chrome Extension API |
| Backend | Python, FastAPI |
| AI Framework | LangChain |
| LLM (answer generation) | OpenRouter (free-tier models) |
| Embeddings | HuggingFace `sentence-transformers` (runs locally, free) |
| Vector Search | FAISS |
| Data Source | YouTube video captions/transcripts |

**Why OpenRouter instead of Gemini directly?** OpenRouter gives access to multiple free LLMs through one API, without needing Google Cloud billing set up. Embeddings run locally via HuggingFace, so nothing there needs an API key either — the only external API call is to OpenRouter for generating the final answer.

## Project Structure

```text
You_bot/
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env
│   └── venv/
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

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/beautygupta2801/YouTube-bot.git
cd YouTube-bot/backend
```

### 2. Set up the backend

Create and activate a virtual environment:

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install fastapi uvicorn python-dotenv youtube-transcript-api langchain-text-splitters langchain-openai langchain-community langchain-huggingface faiss-cpu sentence-transformers
```

### 3. Get a free OpenRouter API key

1. Go to [openrouter.ai](https://openrouter.ai) and sign up (no credit card needed)
2. Go to **Keys** → create a new key

### 4. Configure environment variables

Create a `.env` file inside `backend/`:

```env
OPENROUTER_API_KEY=your_openrouter_key_here
```

Never commit this file. Add to `.gitignore`:
```gitignore
.env
venv/
```

### 5. Run the backend

```bash
python3 app.py
```

You should see:
```text
Server running on http://127.0.0.1:8000
```

Leave this terminal running.

### 6. Load the Chrome extension

1. Open Chrome → go to `chrome://extensions/`
2. Enable **Developer mode** (top right)
3. Click **Load unpacked**
4. Select the `extension/` folder
5. Pin YouBot from the extensions toolbar

### 7. Use it

1. Open a YouTube video **that has captions available** (click the CC icon in the player to check — see note below)
2. Click the YouBot extension icon
3. Type a question
4. Get an answer grounded in the transcript

## API Reference

**Endpoint:** `POST /api/ask`

**Request:**
```json
{
  "video_id": "aircAruvnKk",
  "question": "What is this video about?"
}
```

`video_id` is the part after `v=` in a YouTube URL.

**Response:**
```json
{
  "answer": "The video explains..."
}
```

## ⚠️ Important Limitation: Captions Required

YouBot works by reading a video's **captions/transcript** — it never watches or listens to the video itself. This means:

- **Works:** videos with English (or Hindi) captions — auto-generated or manual
- **Doesn't work:** videos with no captions at all, or captions only in an unsupported language

Check any video by clicking the **CC** button in the YouTube player. If it's greyed out or missing, YouBot can't process that video.

**Known-working test videos:**
```text
aircAruvnKk   — 3Blue1Brown, "But what is a neural network?"
8jPQjjsBbIc   — TED Talk, Ken Robinson
```

## Free-Tier Notes

- **OpenRouter free models change over time.** If you get a `404` error mentioning a model is "unavailable for free," check [openrouter.ai/models](https://openrouter.ai/models), filter by free pricing, and update the `model=` value in `app.py`.
- Free tier: ~50 requests/day, 20/minute. A one-time $10 credit purchase (non-expiring) raises this to 1,000/day if needed.
- Embeddings run entirely on your machine — no rate limits, no cost, ever.

## Security

- API keys must never appear in `popup.js`, `manifest.json`, or any committed file.
- All LLM calls go through the backend — the extension never talks to OpenRouter directly.
- If a key is ever accidentally committed, revoke and rotate it immediately.

## Current Status

Runs locally via Chrome's "Load unpacked" mode + a local FastAPI backend. Not yet published on the Chrome Web Store.

## Future Improvements

- Graceful error message when a video has no usable captions (instead of a raw error)
- Deploy the backend so it doesn't need to run locally
- Add conversational memory for follow-up questions
- Add source timestamps for retrieved transcript sections
- Add a dedicated "Summarize this video" button
- Cache processed transcripts to avoid re-embedding on every restart
- Support more caption languages

## Author

**Beauty Kumari**
B.Tech in Computer Science and Engineering, National Institute of Technology Jalandhar

## Repository

`https://github.com/beautygupta2801/YouTube-bot`

## License

Educational and development purposes.

---

If you find this project useful, consider giving the repository a star.


