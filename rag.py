"""
Run once after scraper.py to build the vector index:
    python3 rag.py
Saves index to jaro_index.faiss and jaro_chunks_indexed.json
"""
import json

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

EMBED_MODEL = "all-MiniLM-L6-v2"  # free, runs locally, no API key needed
INDEX_FILE = "jaro_index.faiss"
CHUNKS_FILE = "jaro_chunks_indexed.json"

_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def build_index():
    with open("jaro_chunks.json") as f:
        chunks = json.load(f)

    texts = [c["text"] for c in chunks]
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True).astype("float32")

    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, INDEX_FILE)
    with open(CHUNKS_FILE, "w") as f:
        json.dump(chunks, f)

    print(f"index built: {index.ntotal} vectors saved to {INDEX_FILE}")


def retrieve(query: str, top_k: int = 4) -> str:
    index = faiss.read_index(INDEX_FILE)
    with open(CHUNKS_FILE) as f:
        chunks = json.load(f)

    model = get_model()
    q_vec = model.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(q_vec)

    _, indices = index.search(q_vec, top_k)
    results = [chunks[i]["text"] for i in indices[0] if i < len(chunks)]
    return "\n\n".join(results)


if __name__ == "__main__":
    build_index()
