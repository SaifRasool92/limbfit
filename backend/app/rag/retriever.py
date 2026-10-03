import os
import chromadb
from chromadb.utils import embedding_functions

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_db")
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection_name = "limbfit_corpus"

_embed_fn = None

def get_embed_fn():
    global _embed_fn
    if _embed_fn is None:
        _embed_fn = embedding_functions.DefaultEmbeddingFunction()
    return _embed_fn

def retrieve(query: str, k: int = 5):
    try:
        collection = chroma_client.get_collection(
            name=collection_name,
            embedding_function=get_embed_fn()
        )
    except Exception:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=k
    )

    retrieved_chunks = []
    if results and 'documents' in results and results['documents']:
        docs  = results['documents'][0]
        metas = results['metadatas'][0]
        for doc, meta in zip(docs, metas):
            retrieved_chunks.append({
                "text":   doc,
                "source": meta.get("source", "Unknown"),
                "page":   meta.get("page", 1)
            })
    return retrieved_chunks
