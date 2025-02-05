# qna_chatbot.py
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph
from typing import List
from typing_extensions import TypedDict
from app.routes.matches import parse_match
from config import CONNECTION_STRING, COLLECTION_NAME
import asyncio

# Konfigurasi OpenAI API Key
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)
web_search = TavilySearchResults(max_results=3)

# Inisialisasi embeddings dan PGVector
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
db = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True
)

class GraphState(TypedDict):
    """
    Merepresentasikan state dari graph.
    """
    question: str
    match_id: str
    response: str
    match: str
    web: list
    context: str
    error: str | None

# Definisikan node untuk LangGraph
def receive_input(state):
    return {"question": state.get("question", ""), "match_id": state.get("match_id", None)}

def ask_match_id(state):
    if "match_id" not in state or not state["match_id"]:
        return {"match_id": input("Masukkan match_id: ")}
    return {}

def perform_web_search(state):
    question = state["question"]
    sapaan = ["hai", "halo", "hey", "hello", "pagi", "siang", "sore", "malam"]
    if question in sapaan:
        return {"web": []}
    result = web_search.invoke(question)
    return {"web": result}

async def perform_api_access(state):
    match_id = state.get("match_id", "")
    try:
        print("DEBUG: Melakukan akses API")
        api_response = await parse_match(match_id)
        if not api_response:
            print("DEBUG: API Response kosong atau None!")

        return {"match": api_response}

    except Exception as e:
        print("DEBUG: Error saat akses API:", str(e))
        return {**state, "match": None, "error": str(e)}

def retrieve_context(state):

    question = state["question"]
    web_result = state.get("web", "")
    match_id = state.get("match_id", "")
    api_data = state.get("match", "")

    try:
        api_context = api_data

        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        query_embedding = embeddings.embed_query(question)

        docs = db.similarity_search_by_vector(
            embedding=query_embedding,
            k=3,
        )

        semantic_context = "\n".join([
            f"Content: {doc.page_content}\nMetadata: {doc.metadata}" 
            for doc in docs
        ])


        final_context = ""
        if api_context:
            final_context += f"\nMatch Information:\n{api_context}"
        if semantic_context:
            final_context += f"\nAdditional Semantic Context:\n{semantic_context}"
        if web_result:
            final_context += f"\nWeb Search Result (Additional Context):\n{web_result}"

        print("DEBUG: Final Context:", final_context)

        return {"context": final_context, "question": question, "error": None, "web": web_result}
    except Exception as e:
        return {"error": str(e), "context": "", "question": question, "match_id": match_id, "web": web_result}

async def generate_response(state):
    if state.get("error"):
        return {"response": f"Maaf, terjadi error: {state['error']}", "error": state['error'], "web": state.get("web", "")}

    context = state["context"]
    question = state["question"]
    match_id = state["match_id"]
    web_result = state.get("web", "")

    try:
        system_prompt = """Anda adalah pelatih Dota 2 profesional SUPER KRITIS dengan analisis tajam dan roasting habis-habisan. Setiap kritik WAJIB disertai:
- Alasan teknis
- Contoh konkret
- Solusi praktis

DRAFT & STRATEGI ROASTING
- Brutal breakdown kelemahan draft
- Roasting draft yang tidak koheren
- Sebut secara spesifik kombinasi hero yang FATAL
- Kritik timing power spike yang buruk

ROASTING PERFORMA INDIVIDUAL
- KDA Analysis: "Ini KDA atau KDA terminal?"
- Positioning Error: "Mau jadi creep atau hero?"
- Farm Efficiency: "Ekonomi kelas pengamen"
- Roasting build item seperti stand-up comedy
- Sebut kerugian finansial dari setiap kesalahan

FASE GAME DESTRUKSI
- Early Game: "Laning kayak main boneka"
- Mid Game: "Rotasi seperti navigasi buta"
- Late Game: "High ground defense mirip pertahanan kardus"

ITEM BUILD ROASTING LEVEL DEWA
- Matematis & pedas
- Hitung kerugian gold dari setiap item buruk
- Rekomendasikan build optimal dengan bukti statistik
- Roasting item seperti critic film

PENGEMBANGAN SKILL
- Roadmap peningkatan killer
- Drill down ke mekanik terburuk
- Rekomendasikan hero untuk "terapi"

KOMUNIKASI
- Bahasa Indonesia super tajam
- Format: Hero Name (Player Name)
- Kritik tanpa ampun
- Solusi 100% praktis"""

        full_prompt = f"{system_prompt}\n\nContext Match ID: {match_id}\n{context}\n\nQuestion: {question}\nAnswer:"

        client = ChatOpenAI(model="gpt-4o-mini")
        response = await client.ainvoke(full_prompt)
        
        return {"response": response.content, "error": None, "web": web_result}
    except Exception as e:
        return {"response": f"Maaf, terjadi error saat generate response: {str(e)}", "error": str(e), "web": web_result}

def create_graph() -> StateGraph:
    workflow = StateGraph(GraphState)

    workflow.add_node("receive_input", receive_input)
    workflow.add_node("ask_match_id", ask_match_id)
    # workflow.add_node("perform_web_search", perform_web_search)
    workflow.add_node("perform_api_access", perform_api_access)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("generate_response", generate_response)
    workflow.set_entry_point("receive_input")

    workflow.add_edge("receive_input", "ask_match_id")
    # workflow.add_edge("ask_match_id", "perform_web_search")
    workflow.add_edge("ask_match_id", "perform_api_access")
    workflow.add_edge("perform_api_access", "retrieve_context")
    workflow.add_edge("retrieve_context", "generate_response")

    workflow.set_finish_point("generate_response")

    return workflow

CURRENT_MATCH_ID = None

async def run_chatbot(question: str) -> str:
    global CURRENT_MATCH_ID
    try:
        workflow = create_graph()
        state = {"question": question}
        if CURRENT_MATCH_ID:
            state["match_id"] = CURRENT_MATCH_ID
        result = await workflow.compile().ainvoke(state)
        if "match_id" in state and state["match_id"]:
            CURRENT_MATCH_ID = state["match_id"]
        return result["response"]
    except Exception as e:
        return f"Terjadi error sistem: {str(e)}"

if __name__ == "__main__":
    async def main():
        while True:
            question = input("You: ")
            if question.lower() in ["exit", "quit"]:
                break
            response = await run_chatbot(question)
            print(f"Bot: {response}")
    
    asyncio.run(main())
