import time

import config
from ingest import embed, get_collection


def retrieve_chunks(query: str) -> dict:
    start = time.time()
    result = get_collection().query(query_embeddings=embed([query]), n_results=config.TOP_K)
    elapsed_ms = round((time.time() - start) * 1000)

    chunks = [
        {
            "content": doc,
            "source": meta["source"],
            "page": meta["page"],
            "relevance_score": round(1 - dist, 4),
        }
        for doc, meta, dist in zip(result["documents"][0], result["metadatas"][0], result["distances"][0])
    ]
    return {
        "query": query,
        "retrieved_chunks": chunks,
        "retrieval_time_ms": elapsed_ms,
        "embedding_model": config.EMBEDDING_MODEL,
    }
