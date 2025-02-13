import asyncio
from typing import AsyncGenerator
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import LLMChain
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableLambda
from langchain_openai.chat_models.base import BaseChatOpenAI

import os
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class PredictionState(BaseModel):
    question: str


async def generate_predictions(question: str, model: str = "gpt-4o-mini") -> AsyncGenerator[str, None]:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    try:
        logger.info(f"Starting prediction for question: {question}")  # Debug log
        if(model == "gpt-4o-mini"):
            logger.info("Using GPT 4o Mini")
            if not os.getenv("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            llm = ChatOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-4o-mini",
                temperature=0.4,
                streaming=True
            )
        elif(model == "gemini-1.5-flash"):
            
            if not os.getenv("GEMINI_API_KEY"):
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            
            logger.info("Using Gemini 1.5 Flash")
            llm = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GEMINI_API_KEY"),
                model="gemini-1.5-flash",
                temperature=0.4,
                stream=True)
        elif(model == "deepseek"):
            logger.info("Using DeepSeek")
            if not os.getenv("DEEPSEEK_API_KEY"):
                raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
            
            llm = BaseChatOpenAI(
               model='deepseek-chat', 
               openai_api_key=os.getenv("DEEPSEEK_API_KEY"), 
               openai_api_base='https://api.deepseek.com',
               temperature=0.4,
               streaming=True)
        else:
            raise ValueError("Invalid model: " + model)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant."),
            ("user", "{question}")
        ])

        handler = AsyncIteratorCallbackHandler()

        passthrough = RunnableLambda(lambda x: x)

        chain = (
            prompt
            | llm
            | passthrough
            | StrOutputParser()
        )
        
        async def run_chain():
            logger.info("Starting chain execution")  # Debug log
            await chain.ainvoke(
                {"question": question}, 
                callbacks=[handler],
                config={"callbacks": [handler]}  # Pastikan callback terdaftar
            )
            logger.info("Chain execution completed")  # Debug log

        task = asyncio.create_task(run_chain())

        logger.info("Starting token stream")  # Debug log
        async for token in handler.aiter():
            logger.info(f"Received token: {token}")  # Debug log
            yield token
        await task
    except asyncio.TimeoutError as te:
        logger.error(f"Timeout error: {str(te)}")  # Debug log
        error_msg = "Request timed out"
        yield f"Error: {error_msg}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")  # Debug log
        error_msg = f"Error in generate_predictions: {str(e)}"
        yield f"Error: {error_msg}"