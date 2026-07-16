
# import os
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from youtube_transcript_api import (
#     YouTubeTranscriptApi,
#     TranscriptsDisabled,
#     NoTranscriptFound
# )
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS
# from langchain_core.prompts import PromptTemplate
# from langchain_core.runnables import (
#     RunnableParallel,
#     RunnablePassthrough,
#     RunnableLambda
# )
# from langchain_core.output_parsers import StrOutputParser
# import uvicorn

# # =========================
# # LOAD ENV VARIABLES
# # =========================
# load_dotenv()

# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# if not OPENROUTER_API_KEY:
#     raise ValueError("OPENROUTER_API_KEY not found in .env file")

# # =========================
# # FASTAPI APP
# # =========================
# app = FastAPI()

# # =========================
# # ENABLE CORS
# # =========================
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # =========================
# # REQUEST MODEL
# # =========================
# class AskRequest(BaseModel):
#     video_id: str
#     question: str

# # =========================
# # CACHE
# # =========================
# video_chains = {}

# # =========================
# # CREATE VIDEO QA CHAIN
# # =========================
# def get_video_chain(video_id: str):

#     # Return cached chain if exists
#     if video_id in video_chains:
#         return video_chains[video_id]

#     try:
#         # Fetch transcript (tries English first, falls back to Hindi)
#         transcript_list = YouTubeTranscriptApi().fetch(
#             video_id,
#             languages=["en", "hi"]
#         )

#         transcript = " ".join(
#             chunk.text for chunk in transcript_list
#         )

#     except TranscriptsDisabled:
#         raise HTTPException(
#             status_code=400,
#             detail="This video has captions disabled by the uploader, so I can't process it. Try a different video."
#         )

#     except NoTranscriptFound:
#         raise HTTPException(
#             status_code=400,
#             detail="This video doesn't have captions in English or Hindi. YouBot only works on videos with captions available — check the CC icon on the video to confirm."
#         )

#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"[DEBUG] {type(e).__name__}: {str(e)}"
#         )

#     # =========================
#     # SPLIT TRANSCRIPT
#     # =========================
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200
#     )

#     chunks = splitter.create_documents([transcript])

#     # =========================
#     # EMBEDDINGS
#     # =========================
#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

#     # =========================
#     # VECTOR STORE
#     # =========================
#     vector_store = FAISS.from_documents(
#         chunks,
#         embeddings
#     )

#     # =========================
#     # RETRIEVER
#     # =========================
#     retriever = vector_store.as_retriever(
#         search_type="similarity",
#         search_kwargs={"k": 4}
#     )

#     # =========================
#     # LLM
#     # =========================
#     llm = ChatOpenAI(
#         model="nvidia/nemotron-3-ultra-550b-a55b:free",
#         temperature=0.3,
#         openai_api_key=OPENROUTER_API_KEY,
#         openai_api_base="https://openrouter.ai/api/v1"
#     )

#     # =========================
#     # PROMPT
#     # =========================
#     prompt = PromptTemplate(
#         template="""
# You are a helpful assistant.

# Answer the user's question ONLY from the context below.

# If the answer is not present in the context, say:
# "I could not find the answer in the video transcript."

# Context:
# {context}

# Question:
# {question}
# """,
#         input_variables=["context", "question"]
#     )

#     # =========================
#     # FORMAT DOCS
#     # =========================
#     def format_docs(retrieved_docs):
#         return "\n\n".join(
#             doc.page_content for doc in retrieved_docs
#         )

#     # =========================
#     # RAG CHAIN
#     # =========================
#     parallel_chain = RunnableParallel({
#         "context": retriever | RunnableLambda(format_docs),
#         "question": RunnablePassthrough()
#     })

#     parser = StrOutputParser()

#     main_chain = (
#         parallel_chain
#         | prompt
#         | llm
#         | parser
#     )

#     # Cache chain
#     video_chains[video_id] = main_chain

#     return main_chain

# # =========================
# # API ROUTE
# # =========================
# @app.post("/api/ask")
# async def ask_question(req: AskRequest):

#     if not req.video_id:
#         raise HTTPException(
#             status_code=400,
#             detail="Please provide a video ID."
#         )

#     if not req.question:
#         raise HTTPException(
#             status_code=400,
#             detail="Please enter a question."
#         )

#     try:
#         chain = get_video_chain(req.video_id)

#         answer = chain.invoke(req.question)

#         return {
#             "answer": answer
#         }

#     except HTTPException:
#         # Let our own clean errors (transcript issues, etc.) pass through unchanged
#         raise

#     except Exception as e:
#         error_msg = str(e)

#         if "404" in error_msg and "unavailable for free" in error_msg:
#             detail = "The AI model is temporarily unavailable on the free tier. Try again in a moment, or check openrouter.ai/models for a current free model."
#         elif "401" in error_msg or "authentication" in error_msg.lower():
#             detail = "Invalid or missing OpenRouter API key. Check your .env file."
#         elif "429" in error_msg:
#             detail = "Rate limit reached. Wait a minute and try again."
#         else:
#             detail = "Something went wrong while generating the answer. Please try again."

#         raise HTTPException(
#             status_code=500,
#             detail=detail
#         )

# # =========================
# # RUN SERVER
# # =========================
# if __name__ == "__main__":
#     print("Server running on http://127.0.0.1:8000")

#     uvicorn.run(
#         app,
#         host="127.0.0.1",
#         port=8000
#     )





###-----updated
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
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

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file")

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
# HELPER: FORMAT SECONDS AS MM:SS
# =========================
def format_timestamp(seconds: float) -> str:
    total_seconds = int(seconds)
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes:02d}:{secs:02d}"

# =========================
# CREATE VIDEO QA CHAIN
# =========================
def get_video_chain(video_id: str):

    # Return cached chain if exists
    if video_id in video_chains:
        return video_chains[video_id]

    try:
        # Fetch transcript (tries English first, falls back to Hindi)
        transcript_list = YouTubeTranscriptApi().fetch(
            video_id,
            languages=["en", "hi"]
        )

        # Keep timestamps attached to each line of text.
        # Each line now looks like: "[02:15] some spoken text here"
        transcript = "\n".join(
            f"[{format_timestamp(chunk.start)}] {chunk.text}"
            for chunk in transcript_list
        )

    except TranscriptsDisabled:
        raise HTTPException(
            status_code=400,
            detail="This video has captions disabled by the uploader, so I can't process it. Try a different video."
        )

    except NoTranscriptFound:
        raise HTTPException(
            status_code=400,
            detail="This video doesn't have captions in English or Hindi. YouBot only works on videos with captions available — check the CC icon on the video to confirm."
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Couldn't fetch the transcript for this video. It may be private, age-restricted, or unavailable. Try a different video."
        )

    # =========================
    # SPLIT TRANSCRIPT
    # =========================
    # Slightly larger chunks + more overlap so each chunk still contains
    # enough surrounding [MM:SS] markers for the model to reference.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=300,
        separators=["\n", ". ", " ", ""]
    )

    chunks = splitter.create_documents([transcript])

    # =========================
    # EMBEDDINGS
    # =========================
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

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
    llm = ChatOpenAI(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        temperature=0.3,
        openai_api_key=OPENROUTER_API_KEY,
        openai_api_base="https://openrouter.ai/api/v1"
    )

    # =========================
    # PROMPT
    # =========================
    prompt = PromptTemplate(
        template="""
You are a helpful assistant answering questions about a YouTube video.

The context below contains lines from the video transcript. Each line starts
with a timestamp in [MM:SS] format showing when that part was spoken.

Answer the user's question ONLY using the context below.
If the question asks about a specific time, moment, or "what was taught/said
at X", mention the relevant [MM:SS] timestamp(s) in your answer.

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
            detail="Please provide a video ID."
        )

    if not req.question:
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        chain = get_video_chain(req.video_id)

        answer = chain.invoke(req.question)

        return {
            "answer": answer
        }

    except HTTPException:
        # Let our own clean errors (transcript issues, etc.) pass through unchanged
        raise

    except Exception as e:
        error_msg = str(e)

        if "404" in error_msg and "unavailable for free" in error_msg:
            detail = "The AI model is temporarily unavailable on the free tier. Try again in a moment, or check openrouter.ai/models for a current free model."
        elif "401" in error_msg or "authentication" in error_msg.lower():
            detail = "Invalid or missing OpenRouter API key. Check your .env file."
        elif "429" in error_msg:
            detail = "Rate limit reached. Wait a minute and try again."
        else:
            detail = "Something went wrong while generating the answer. Please try again."

        raise HTTPException(
            status_code=500,
            detail=detail
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