import os
import glob
import chromadb
from chromadb.utils import embedding_functions

# Setup ChromaDB persistent client
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
os.makedirs(DB_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection_name = "limbfit_corpus"

def chunk_text(text, chunk_size=500, overlap=80):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def get_embedding_fn():
    """Use ChromaDB's built-in ONNX-based embedding (no PyTorch needed)."""
    return embedding_functions.DefaultEmbeddingFunction()

def ingest_corpus(corpus_dir: str = None):
    if corpus_dir is None:
        corpus_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "data", "corpus"
        )

    embed_fn = get_embedding_fn()
    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn
    )

    documents = []
    metadatas = []
    ids = []

    txt_files = glob.glob(os.path.join(corpus_dir, "**", "*.txt"), recursive=True)
    md_files  = glob.glob(os.path.join(corpus_dir, "**", "*.md"),  recursive=True)
    all_files = txt_files + md_files
    print(f"Found {len(all_files)} documents to ingest.")

    for file_path in all_files:
        filename = os.path.basename(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({"source": filename, "page": 1, "chunk_idx": i})
            ids.append(f"{filename}_chunk_{i}")

    if documents:
        print(f"Embedding and storing {len(documents)} chunks…")
        batch_size = 50
        for i in range(0, len(documents), batch_size):
            collection.add(
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size],
                ids=ids[i:i + batch_size]
            )
        print("Ingestion complete.")
    else:
        print("No documents found to ingest.")

if __name__ == "__main__":
    ingest_corpus()
