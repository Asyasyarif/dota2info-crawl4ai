# qna_chatbot.py
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langgraph.graph import Graph

from config import CONNECTION_STRING, COLLECTION_NAME
# Konfigurasi OpenAI API Key
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)


# Inisialisasi embeddings dan PGVector
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
db = PGVector(
    embeddings=embeddings,
    collection_name=COLLECTION_NAME,
    connection=CONNECTION_STRING,
    use_jsonb=True
)

# Definisikan node untuk LangGraph
def receive_input(state):
    return {"question": state.get("question", "")}

def retrieve_context(state):
    question = state["question"]
    
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        query_embedding = embeddings.embed_query(question)

        docs = db.similarity_search_by_vector(
            embedding=query_embedding,
            k=3,
        )
        
        context = "\n".join([
            f"Content: {doc.page_content}\nMetadata: {doc.metadata}" 
            for doc in docs
        ])
        
        return {"context": context, "question": question, "error": None}
    except Exception as e:
        return {"error": str(e), "context": "", "question": question}

def generate_response(state):
    if state.get("error"):
        return {"response": f"Maaf, terjadi error: {state['error']}"}
        
    context = state["context"]
    question = state["question"]
    
    try:
        system_prompt = """Anda adalah coach Dota 2 profesional. 
        Jawab pertanyaan dengan:
        1. Analisis berdasarkan data game terbaru
        2. Referensi hero/item yang relevan
        3. Strategi berdasarkan role (carry/support/mid)
        Gunakan bahasa Indonesia informal, gaul, dan mudah dimengerti."""
        
        full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"
        
        client = ChatOpenAI(model="gpt-4o-mini")
        response = client.invoke(full_prompt)
        
        return {"response": response.content, "error": None}
    except Exception as e:
        return {"response": f"Maaf, terjadi error saat generate response: {str(e)}", "error": str(e)}

# Buat grafik alur kerja dengan LangGraph
def create_graph() -> Graph:
    workflow = Graph()
    
    # Tambahkan nodes
    workflow.add_node("receive_input", receive_input)
    workflow.add_node("retrieve_context", retrieve_context)
    workflow.add_node("generate_response", generate_response)

    # Set entry dan finish points
    workflow.set_entry_point("receive_input")
    workflow.set_finish_point("generate_response")
    
    # Tambahkan edges dengan conditional routing
    workflow.add_edge("receive_input", "retrieve_context")
    workflow.add_edge("retrieve_context", "generate_response")

    return workflow

def run_chatbot(question: str) -> str:
    try:
        workflow = create_graph()
        state = {"question": question}
        result = workflow.compile().invoke(state)
        return result["response"]
    except Exception as e:
        return f"Terjadi error sistem: {str(e)}"


if __name__ == "__main__":
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            break
        response = run_chatbot(question)
        print(f"Bot: {response}")
