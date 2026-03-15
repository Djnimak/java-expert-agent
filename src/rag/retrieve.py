from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.config import QDRANT_URL, COLLECTION_NAME, TOP_K_RESULTS


def retrieve_relevant_chunks(
    question: str,
    embedding_model: SentenceTransformer,
    qdrant_client: QdrantClient,
    collection_name: str = COLLECTION_NAME,
    top_k: int = TOP_K_RESULTS,
) -> list[dict]:
    """
    Retrieve the most relevant chunks from Qdrant for a given question.
    """
    question_vector = embedding_model.encode(
        question,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).tolist()

    search_result = qdrant_client.query_points(
        collection_name=collection_name,
        query=question_vector,
        limit=top_k,
    )

    retrieved_chunks: list[dict] = []

    for hit in search_result.points:
        payload = hit.payload or {}

        retrieved_chunks.append(
            {
                "score": hit.score,
                "source_type": payload.get("source_type", "unknown"),
                "file_name": payload.get("file_name", "unknown"),
                "chunk_index": payload.get("chunk_index", -1),
                "text": payload.get("text", ""),
            }
        )

    return retrieved_chunks