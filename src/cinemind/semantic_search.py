from src.cinemind.embedding_client import client, index, get_embeddings_batch

def semantic_search(query, top_k=10):

    query_embedding = get_embeddings_batch(
        [query]
    )[0]

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results