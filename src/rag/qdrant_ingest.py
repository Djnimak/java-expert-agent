from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from src.config import (
    QDRANT_URL,
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
)
from src.rag.ingest import load_all_documents, build_chunk_records


def load_chunk_records(project_root: Path) -> list[dict]:
    documents = load_all_documents(project_root)

    chunk_records = build_chunk_records(
        documents=documents,
        chunk_size=CHUNK_SIZE,
        overlap=CHUNK_OVERLAP,
    )

    return chunk_records


def create_embeddings(
    model: SentenceTransformer,
    chunk_records: list[dict],
) -> list[list[float]]:
    texts = [record["text"] for record in chunk_records]

    print(f"Creating embeddings for {len(texts)} chunks...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()


def recreate_collection(
    client: QdrantClient,
    collection_name: str,
    vector_size: int,
) -> None:
    if client.collection_exists(collection_name):
        print(f"Collection '{collection_name}' already exists. Deleting it first...")
        client.delete_collection(collection_name=collection_name)

    print(f"Creating collection '{collection_name}' with vector size {vector_size}...")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE,
        ),
    )


def upload_points(
    client: QdrantClient,
    collection_name: str,
    chunk_records: list[dict],
    embeddings: list[list[float]],
) -> None:
    points: list[PointStruct] = []

    for idx, (record, vector) in enumerate(zip(chunk_records, embeddings)):
        payload = {
            "source_type": record["source_type"],
            "file_name": record["file_name"],
            "chunk_index": record["chunk_index"],
            "text": record["text"],
        }

        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload=payload,
            )
        )

    print(f"Uploading {len(points)} points to Qdrant...")

    client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points,
    )


def main() -> None:
    print("Java Expert Agent - Qdrant ingestion started")

    project_root = Path(__file__).resolve().parent.parent.parent

    chunk_records = load_chunk_records(project_root)
    print(f"Total chunk records: {len(chunk_records)}")

    if not chunk_records:
        raise ValueError("No chunk records were created.")

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")

    embeddings = create_embeddings(model, chunk_records)

    if not embeddings:
        raise ValueError("No embeddings were created.")

    vector_size = len(embeddings[0])
    print(f"Embedding vector size: {vector_size}")

    client = QdrantClient(url=QDRANT_URL)
    print(f"Connected to Qdrant at: {QDRANT_URL}")

    recreate_collection(client, COLLECTION_NAME, vector_size)
    upload_points(client, COLLECTION_NAME, chunk_records, embeddings)

    print("Qdrant ingestion completed successfully.")
    print(f"Collection name: {COLLECTION_NAME}")
    print(f"Stored points: {len(chunk_records)}")


if __name__ == "__main__":
    main()