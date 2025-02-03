import logging
from dotenv import load_dotenv
from pathlib import Path
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters.markdown import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from config import CONNECTION_STRING, COLLECTION_NAME

# Load environment variables
env_path = Path('.env')
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BATCH_SIZE = 50  # Tambahkan konstanta batch size

def create_hero_embeddings():
    try:
        # Load semua file markdown dari folder heroes
        loader = DirectoryLoader(
            "./heroes/7.37e",
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        # Split dokumen markdown berdasarkan headers
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on
        )

        # Proses semua dokumen
        all_splits = []
        for doc in documents:
            try:
                splits = markdown_splitter.split_text(doc.page_content)
                # Tambahkan metadata dari dokumen asli ke setiap split
                for split in splits:
                    split.metadata.update(doc.metadata)
                all_splits.extend(splits)
            except Exception as e:
                logging.error(f"Error memproses dokumen {doc.metadata.get('source')}: {str(e)}")
                continue
        
        logging.info(f"Total dokumen: {len(documents)}")
        logging.info(f"Total chunks: {len(all_splits)}")

        # Buat embeddings menggunakan OpenAI
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

        # Inisialisasi PGVector
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=COLLECTION_NAME,
            connection=CONNECTION_STRING,
            pre_delete_collection=True,
            use_jsonb=True
        )

        # Tambahkan dokumen dalam batch
        total_docs = len(all_splits)
        for i in range(0, total_docs, BATCH_SIZE):
            batch = all_splits[i:i+BATCH_SIZE]
            vector_store.add_documents(documents=batch)
            logging.info(f"Proses batch {i//BATCH_SIZE + 1}/{(total_docs-1)//BATCH_SIZE + 1} selesai")

        logging.info("Embeddings berhasil disimpan ke PGVector!")
    
    except Exception as e:
        logging.error(f"Error saat membuat embeddings: {str(e)}")

if __name__ == "__main__":
    create_hero_embeddings()