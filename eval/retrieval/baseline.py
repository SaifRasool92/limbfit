import os
import json
import numpy as np
import chromadb
from chromadb.utils import embedding_functions

def evaluate(test_file, db_path, collection_name="limbfit_corpus"):
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        print("Run make_dataset.py first.")
        return None

    queries = []
    contexts = []
    with open(test_file, 'r') as f:
        for line in f:
            data = json.loads(line.strip())
            queries.append(data["query"])
            contexts.append(data["context"])

    if not queries:
        print("No test data found.")
        return None

    print(f"Evaluating on {len(queries)} test queries…")

    embed_fn = embedding_functions.DefaultEmbeddingFunction()

    client = chromadb.PersistentClient(path=db_path)
    try:
        collection = client.get_collection(name=collection_name, embedding_function=embed_fn)
    except Exception as e:
        print(f"Collection not found: {e}. Run ingest first.")
        return None

    metrics = {"recall@1": 0, "recall@3": 0, "recall@5": 0, "mrr": 0.0}

    for i, query in enumerate(queries):
        true_context = contexts[i]
        results = collection.query(query_texts=[query], n_results=min(5, collection.count()))
        retrieved_docs = results["documents"][0] if results["documents"] else []

        found_rank = None
        for rank, doc in enumerate(retrieved_docs, 1):
            if doc.strip() == true_context.strip():
                found_rank = rank
                break

        if found_rank is not None:
            if found_rank == 1: metrics["recall@1"] += 1
            if found_rank <= 3: metrics["recall@3"] += 1
            if found_rank <= 5: metrics["recall@5"] += 1
            metrics["mrr"] += 1.0 / found_rank

    n = len(queries)
    for k in metrics:
        metrics[k] /= n

    print("Results:")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    return metrics

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    test_file = os.path.join(os.path.dirname(__file__), "test.jsonl")
    db_path   = os.path.join(base_dir, "backend", "chroma_db")
    out_csv   = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results", "retrieval_baseline.csv")

    os.makedirs(os.path.dirname(out_csv), exist_ok=True)

    metrics = evaluate(test_file, db_path)
    if metrics:
        with open(out_csv, 'w') as f:
            f.write("model,recall@1,recall@3,recall@5,mrr\n")
            f.write(f"chroma-default,{metrics['recall@1']:.4f},{metrics['recall@3']:.4f},{metrics['recall@5']:.4f},{metrics['mrr']:.4f}\n")
        print(f"Saved to {out_csv}")

if __name__ == "__main__":
    main()
