# qna_chatbot.py
import os
from dotenv import load_dotenv
import json
import time
import concurrent.futures
from typing import Dict
from pathlib import Path
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_community.tools import TavilySearchResults
from langgraph.graph import StateGraph, START, END
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

class AnalysisState(TypedDict):
    question: str
    match_data: Dict
    results: Dict[str, Dict]
    selected_nodes: List[str]
    error: str | None

def analyze_hero_composition(state: AnalysisState) -> dict:
    print("Memproses analisis komposisi hero...")
    hero_composition = {
        "hero_composition": {
            "radiant": ["Axe", "Lina", "Crystal Maiden", "Juggernaut", "Shadow Shaman"],
            "dire": ["Tidehunter", "Invoker", "Lion", "Phantom Assassin", "Witch Doctor"]
        }
    }
    return hero_composition

def analyze_item_build(state: AnalysisState) -> dict:
    print("Memproses analisis item build...")
    time.sleep(1)
    return {"item_build": "Hasil analisis item build"}

def analyze_stats(state: AnalysisState) -> dict:
    print("Memproses analisis statistik...")
    stats = {
        "stats": {
            "radiant": {
                "gold": 10000,
                "kills": 10,
                "deaths": 5,
                "assists": 3
            },
            "dire": {
                "gold": 8000,
                "kills": 8,
                "deaths": 6,
                "assists": 2
            }
        }
    }
    return stats

def analyze_timeline(state: AnalysisState) -> dict:
    print("Memproses analisis timeline...")
    time.sleep(1)
    return {"timeline": "Hasil analisis timeline"}

def analyze_key_events(state: AnalysisState) -> dict:
    print("Memproses analisis peristiwa kunci...")
    time.sleep(1)
    return {"key_events": "Hasil analisis peristiwa kunci"}

def auto_select_nodes(state: AnalysisState) -> dict:
    print("Memproses seleksi analisis otomatis...")
    question = state["question"]
    prompt = f"""
    Kamu adalah asisten analisis Dota 2. Berdasarkan query berikut: "{question}",
    tentukan node analisis apa saja yang harus dijalankan dari daftar berikut:
    ["hero_composition", "item_build", "stats", "timeline", "key_events"].
    Jawab hanya dalam format JSON list. Contoh: ["hero_composition", "stats"]
    """
    try:
        client = ChatOpenAI(openai_api_key=os.getenv("DEEPSEEK_API_KEY"), 
                           openai_api_base='https://api.deepseek.com', 
                           model="deepseek-chat", 
                           max_tokens=100, 
                           temperature=0)
        response = client.invoke(prompt)
        cleaned_content = response.content.strip()
        if cleaned_content.startswith("```") and cleaned_content.endswith("```"):
            cleaned_content = cleaned_content[3:-3].strip()
        selected_nodes = json.loads(cleaned_content)
        allowed = {"hero_composition", "item_build", "stats", "timeline", "key_events"}

        if not isinstance(selected_nodes, list):
            return {"error": "Format jawaban tidak valid", "selected_nodes": []}

        if not all(node in allowed for node in selected_nodes):
            return {"error": "Format jawaban tidak valid", "selected_nodes": []}

        return {"selected_nodes": selected_nodes}
    except Exception as e:
        print(f"Error in auto_select_nodes: {str(e)}")
        return {"error": str(e), "selected_nodes": ["hero_composition", "stats"]}

def run_parallel_analysis(state: AnalysisState) -> dict:
    """
    Node ini akan mengambil nilai match_data dan daftar selected_nodes dari state,
    lalu menjalankan fungsi-fungsi analisis yang terpilih secara paralel.
    Hasil masing-masing node akan dikumpulkan ke dalam state["results"].
    """

    nodes = {
        "hero_composition": analyze_hero_composition,
        "item_build": analyze_item_build,
        "stats": analyze_stats,
        "timeline": analyze_timeline,
        "key_events": analyze_key_events,
    }
    print("Running parallel analysis...")
    print(state["selected_nodes"])
    selected = state["selected_nodes"]
    results = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_node = {}
        for key in selected:
            if key in nodes:
                future = executor.submit(nodes[key], state)
                future_to_node[future] = key
            else:
                print(f"Warning: Node '{key}' tidak ditemukan.")
        for future in concurrent.futures.as_completed(future_to_node):
            node_name = future_to_node[future]
            try:
                res = future.result()
                results[node_name] = res
                print(f"Node '{node_name}' selesai dengan hasil: {res}")
            except Exception as exc:
                print(f"Node '{node_name}' menghasilkan exception: {exc}")
    return {"results": results}

def receive_input(state):
    return {"question": state.get("question", "")}

def retrieve_context(state):
    question = state["question"]
    match_data = state.get("match_data")

    try:
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

        if semantic_context:
            final_context += f"\nAdditional Semantic Context:\n{semantic_context}"
        if match_data:
            final_context += f"\nGame Match Information:\n{match_data}"

        return {"context": final_context, "error": None}
    except Exception as e:
        return {"error": str(e), "context": ""}

async def generate_response(state):
    if state.get("error"):
        return {"response": f"Maaf, terjadi error: {state['error']}", "error": state['error']}

    context = state["context"]
    question = state["question"]
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
- Bahasa Indonesia gaul dan super tajam
- Format: Hero Name (Player Name)
- Kritik tanpa ampun
- Solusi 100% praktis"""

        full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

        client = ChatOpenAI(openai_api_key=os.getenv("DEEPSEEK_API_KEY"), openai_api_base='https://api.deepseek.com', model="deepseek-chat", max_tokens=4000)
        response = await client.ainvoke(full_prompt)

        return {"response": response.content, "error": None}
    except Exception as e:
        return {"response": f"Maaf, terjadi error saat generate response: {str(e)}", "error": str(e)}

def create_graph() -> StateGraph:
    workflow = StateGraph(AnalysisState)

    workflow.add_node(receive_input)
    workflow.add_node("auto_select_analysis", auto_select_nodes)
    workflow.add_node("run_parallel_analysis", run_parallel_analysis)
    workflow.add_node("generate_response", generate_response)
    workflow.set_entry_point("receive_input")

    workflow.add_edge(START, "receive_input")
    workflow.add_edge("receive_input", "auto_select_analysis")
    workflow.add_edge("auto_select_analysis", "run_parallel_analysis")
    workflow.add_edge("run_parallel_analysis", "generate_response")
    workflow.add_edge("generate_response", END)

    workflow.set_finish_point("generate_response")

    return workflow

async def run_chatbot(question: str, match_data: dict) -> str:
    try:
        workflow = create_graph()
        state = {
            "question": question,
            "match_data": match_data,
            "results": {},
            "selected_nodes": [],
            "error": None
        }
        result = await workflow.compile().ainvoke(state)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

# if __name__ == "__main__":
#     async def main():
#         while True:
#             question = input("You: ")
#             if question.lower() in ["exit", "quit"]:
#                 break
#             response = await run_chatbot(question)
#             print(f"Bot: {response}")

#     asyncio.run(main())
