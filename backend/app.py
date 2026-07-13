import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda
)
from langchain_core.output_parsers import StrOutputParser
import uvicorn

# =========================
# LOAD ENV VARIABLES
# =========================
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

# =========================
# FASTAPI APP
# =========================
app = FastAPI()

# =========================
# ENABLE CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# REQUEST MODEL
# =========================
class AskRequest(BaseModel):
    video_id: str
    question: str

# =========================
# CACHE
# =========================
video_chains = {}

# =========================
# CREATE VIDEO QA CHAIN
# =========================
def get_video_chain(video_id: str):

    # Return cached chain if exists
    if video_id in video_chains:
        return video_chains[video_id]

    try:
        # Fetch transcript
        transcript_list = YouTubeTranscriptApi().fetch(
            video_id,
            languages=["en"]
        )

        transcript = " ".join(
            chunk.text for chunk in transcript_list
        )

    except TranscriptsDisabled:
        raise HTTPException(
            status_code=400,
            detail="No captions available for this video."
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching transcript: {str(e)}"
        )

    # =========================
    # SPLIT TRANSCRIPT
    # =========================
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.create_documents([transcript])

    # =========================
    # EMBEDDINGS
    # =========================
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )

    # =========================
    # VECTOR STORE
    # =========================
    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    # =========================
    # RETRIEVER
    # =========================
    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4}
    )

    # =========================
    # LLM
    # =========================
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    # =========================
    # PROMPT
    # =========================
    prompt = PromptTemplate(
        template="""
You are a helpful assistant.

Answer the user's question ONLY from the context below.

If the answer is not present in the context, say:
"I could not find the answer in the video transcript."

Context:
{context}

Question:
{question}
""",
        input_variables=["context", "question"]
    )

    # =========================
    # FORMAT DOCS
    # =========================
    def format_docs(retrieved_docs):
        return "\n\n".join(
            doc.page_content for doc in retrieved_docs
        )

    # =========================
    # RAG CHAIN
    # =========================
    parallel_chain = RunnableParallel({
        "context": retriever | RunnableLambda(format_docs),
        "question": RunnablePassthrough()
    })

    parser = StrOutputParser()

    main_chain = (
        parallel_chain
        | prompt
        | llm
        | parser
    )

    # Cache chain
    video_chains[video_id] = main_chain

    return main_chain

# =========================
# API ROUTE
# =========================
@app.post("/api/ask")
async def ask_question(req: AskRequest):

    if not req.video_id:
        raise HTTPException(
            status_code=400,
            detail="video_id is required"
        )

    if not req.question:
        raise HTTPException(
            status_code=400,
            detail="question is required"
        )

    try:
        chain = get_video_chain(req.video_id)

        answer = chain.invoke(req.question)

        return {
            "answer": answer
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    print("Server running on http://127.0.0.1:8000")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )