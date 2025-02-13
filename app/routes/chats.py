from fastapi import APIRouter, HTTPException, Request
from app.routes.matches import parse_match
from fastapi.responses import StreamingResponse
from qna import run_chatbot
import asyncio
import random
from app.ai.predictions import generate_predictions
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chats", tags=["chats"])

@router.post("/")
async def start_chat(request: Request):
    data = await request.json()
    match_id = data.get("match_id")
    question = data.get("question")

    if not match_id:
        raise HTTPException(status_code=422, detail="Match ID is required")

    if not question:
        raise HTTPException(status_code=422, detail="Question is required")

    # match = await parse_match(match_id)
    # if not match:
    #     raise HTTPException(status_code=404, detail="Match not found")

    match = None
    response = await run_chatbot(question, match)

    try:
        results = json.loads(response)
    except json.JSONDecodeError:
        if not response:
            results = {}
        else:
            results = {"error": str(response)}

    return {"response": results}

async def generate_sse_events(question: str, model: str) -> AsyncGenerator[str, None]:
    """
    Generate SSE events from prediction messages.
    Args:
        question (str): The question to generate predictions for
    Yields:
        str: Formatted SSE events
    """
    try:
        async for message in generate_predictions(question, model):
            if message == "[DONE]":
                yield f"data: [DONE]\n\n"
                break
            if message.startswith("Error:"):
                logger.error(f"Prediction error: {message}")
                yield f"data: {message}\n\n"
                yield f"data: [DONE]\n\n"
                break
            yield message
            await asyncio.sleep(0.02)

    except asyncio.CancelledError:
        logger.info("Client disconnected")
        yield f"data: [DONE]\n\n"
    except Exception as e:
        logger.error(f"Stream generation error: {str(e)}")
        yield f"data: Error: {str(e)}\n\n"
        yield f"data: [DONE]\n\n"

@router.get("/chat-match")
async def start_chat(
    request: Request,
    question: str
):
    """
    Start a chat session with SSE response.

    Args:
        request (Request): The FastAPI request object
        question (str): The question to ask (optional)

    Returns:
        StreamingResponse: Server-Sent Events stream
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return StreamingResponse(
        generate_sse_events(question=question, model="gpt-4o-mini"),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no',
            'Content-Type': 'text/event-stream',
            'Transfer-Encoding': 'chunked'
        }
    )