"""
Deterministic question dataset generator for RAG evaluation.
No LLM API key required — generates synthetic questions from corpus chunks
using keyword extraction and template patterns. This is sufficient for
evaluating retrieval quality (Recall@K, MRR) in a hackathon setting.

Templates include English and Roman Urdu questions per project requirements.
"""
import os
import glob
import json
import random
import re

# English question templates — {kw} is filled with a keyword from the chunk
ENGLISH_TEMPLATES = [
    "What is the recommended {kw} for a transradial prosthetic socket?",
    "How should a prosthetist handle {kw} when fitting a socket?",
    "What are the guidelines for {kw} in 3D printed sockets?",
    "What happens if {kw} is not done correctly during socket fabrication?",
    "How much {kw} is needed for a properly fitted transradial socket?",
    "What material should be used for {kw} in prosthetic sockets?",
    "Why is {kw} important in socket design for rural patients?",
]

# Roman Urdu templates for i18n compliance
ROMAN_URDU_TEMPLATES = [
    "{kw} ke liye kya standard hai socket design mein?",
    "Transradial socket mein {kw} kaise karna chahiye?",
    "{kw} ki wajah se kya masla ho sakta hai?",
    "3D printed socket ke liye {kw} ki setting kya honi chahiye?",
]

STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could", "to", "of", "in",
    "on", "at", "by", "for", "with", "about", "as", "into", "through",
    "during", "before", "after", "above", "below", "from", "up", "down",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "each", "all", "any", "both", "few", "more", "most", "other", "some",
    "such", "than", "too", "very", "just", "if", "this", "that", "these",
    "those", "it", "its", "they", "them", "their", "use", "used", "using",
    "also", "no", "only", "same", "than", "then", "when", "where", "which",
    "while", "who", "whom", "whose", "how", "what", "why",
}


def extract_keywords(text: str, top_n: int = 8) -> list:
    """Extract meaningful keywords from a text chunk."""
    words = re.findall(r'\b[a-z][a-z\-]+\b', text.lower())
    # Score by frequency, excluding stopwords and very short words
    freq = {}
    for w in words:
        if w not in STOPWORDS and len(w) > 4:
            freq[w] = freq.get(w, 0) + 1
    # Also extract multi-word noun phrases (2-word sequences)
    bigrams = []
    tokens = [w for w in words if w not in STOPWORDS and len(w) > 3]
    for i in range(len(tokens) - 1):
        bigrams.append(f"{tokens[i]} {tokens[i+1]}")
    for bg in bigrams:
        freq[bg] = freq.get(bg, 0) + 0.5
    sorted_kws = sorted(freq.items(), key=lambda x: -x[1])
    return [kw for kw, _ in sorted_kws[:top_n]]


def generate_questions(chunk: str, n: int = 3) -> list:
    """Generate n synthetic questions from a chunk without any LLM."""
    keywords = extract_keywords(chunk)
    if not keywords:
        return []

    questions = []
    used_templates = set()

    # 2 English + 1 Roman Urdu
    all_templates = [
        (ENGLISH_TEMPLATES, 2),
        (ROMAN_URDU_TEMPLATES, 1),
    ]

    for templates, count in all_templates:
        available = [t for t in templates if t not in used_templates]
        random.shuffle(available)
        kw_pool = keywords.copy()
        random.shuffle(kw_pool)
        for template in available[:count]:
            if kw_pool:
                kw = kw_pool.pop(0)
                questions.append(template.format(kw=kw))
                used_templates.add(template)

    return questions[:n]


def chunk_text(text, chunk_size=500, overlap=80):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def main():
    corpus_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "corpus"
    )
    out_dir = os.path.dirname(__file__)

    files = (
        glob.glob(os.path.join(corpus_dir, "**", "*.txt"), recursive=True) +
        glob.glob(os.path.join(corpus_dir, "**", "*.md"),  recursive=True)
    )

    all_chunks = []
    for f in files:
        filename = os.path.basename(f)
        with open(f, 'r') as fh:
            text = fh.read()
        for chunk in chunk_text(text):
            all_chunks.append({"doc": filename, "text": chunk})

    if not all_chunks:
        print("No corpus files found. Add .txt or .md files to data/corpus/")
        return

    random.seed(42)  # reproducible splits
    random.shuffle(all_chunks)
    n = len(all_chunks)
    splits = {
        "train": all_chunks[:int(n * 0.7)],
        "val":   all_chunks[int(n * 0.7):int(n * 0.85)],
        "test":  all_chunks[int(n * 0.85):]
    }

    total_written = 0
    print(f"Generating synthetic questions for {n} chunks (no API key needed)…")
    for split_name, items in splits.items():
        out_path = os.path.join(out_dir, f"{split_name}.jsonl")
        count = 0
        with open(out_path, 'w') as out_f:
            for item in items:
                qs = generate_questions(item["text"])
                for q in qs:
                    out_f.write(json.dumps({
                        "query": q,
                        "context": item["text"],
                        "doc": item["doc"]
                    }) + "\n")
                    count += 1
        print(f"  {split_name}: {len(items)} chunks → {count} Q&A pairs → {split_name}.jsonl")
        total_written += count

    print(f"Done. {total_written} total Q&A pairs written.")


if __name__ == "__main__":
    main()
