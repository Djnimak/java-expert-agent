import os
from pathlib import Path

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

from src.agent.orchestrator import classify_request
from src.agent.reflection_engine import refine_with_reflection
from src.agent.reflection import (
    best_kb_score,
    ensure_general_knowledge_label,
    is_kb_strong_enough,
    is_model_knowledge_strong_enough,
)
from src.agent.tools import (
    answer_from_internal_kb,
    answer_from_model_knowledge,
    answer_from_web_search,
    build_context_from_chunks,
    generate_java_code,
    review_java_code,
)
from src.config import (
    COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    QDRANT_URL,
)
from src.rag.retrieve import retrieve_relevant_chunks


def load_environment() -> None:
    project_root = Path(__file__).resolve().parent.parent
    env_path = project_root / ".env"

    load_dotenv(env_path)

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY was not found in .env file")


def print_retrieved_chunks(chunks: list[dict], preview_length: int = 400) -> None:
    print("\n===== RETRIEVED CHUNKS =====")

    if not chunks:
        print("No chunks retrieved.")
        return

    for index, chunk in enumerate(chunks, start=1):
        print(f"\nChunk {index}")
        print(f"Score: {chunk['score']}")
        print(f"Source type: {chunk['source_type']}")
        print(f"File name: {chunk['file_name']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print("Preview:")
        print(chunk["text"][:preview_length])
        print("\n" + "=" * 60)


def handle_question_answering(user_input: str) -> str:
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    print(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")

    qdrant_client = QdrantClient(url=QDRANT_URL)
    print(f"Connected to Qdrant at: {QDRANT_URL}")
    print(f"Using collection: {COLLECTION_NAME}")

    retrieved_chunks = retrieve_relevant_chunks(
        question=user_input,
        embedding_model=embedding_model,
        qdrant_client=qdrant_client,
    )

    print_retrieved_chunks(retrieved_chunks)

    kb_score = best_kb_score(retrieved_chunks)
    print(f"\nBest KB retrieval score: {kb_score}")

    if is_kb_strong_enough(retrieved_chunks):
        print("Decision: using internal knowledge base.")
        context = build_context_from_chunks(retrieved_chunks)
        draft_answer = answer_from_internal_kb(user_input, context)
    else:
        print("Decision: KB is weak, trying general model knowledge.")
        model_answer = answer_from_model_knowledge(user_input)

        if is_model_knowledge_strong_enough(model_answer):
            print("Decision: using general model knowledge.")
            draft_answer = ensure_general_knowledge_label(model_answer)
        else:
            print("Decision: model knowledge still weak, using web search.")
            draft_answer = answer_from_web_search(user_input)

    final_answer, reflection_text = refine_with_reflection(
        task_type="question_answering",
        user_input=user_input,
        draft_output=draft_answer,
    )

    print("\n===== REFLECTION =====\n")
    print(reflection_text)

    return final_answer


def handle_code_generation(user_input: str) -> str:
    print("Decision: using Java code generation tool.")
    draft_answer = generate_java_code(user_input)

    final_answer, reflection_text = refine_with_reflection(
        task_type="code_generation",
        user_input=user_input,
        draft_output=draft_answer,
    )

    print("\n===== REFLECTION =====\n")
    print(reflection_text)

    return final_answer


def handle_code_review(user_input: str) -> str:
    print("Decision: using Java code review tool.")
    draft_answer = review_java_code(user_input)

    final_answer, reflection_text = refine_with_reflection(
        task_type="code_review",
        user_input=user_input,
        draft_output=draft_answer,
    )

    print("\n===== REFLECTION =====\n")
    print(reflection_text)

    return final_answer


def main() -> None:
    print("Java Expert Agent - classification and code generation test started")

    load_environment()

    user_input = input("Enter your request: ").strip()
    if not user_input:
        raise ValueError("Request cannot be empty")

    request_type = classify_request(user_input)
    print(f"Detected request type: {request_type}")

    if request_type == "question_answering":
        answer = handle_question_answering(user_input)
    elif request_type == "code_generation":
        answer = handle_code_generation(user_input)
    elif request_type == "code_review":
        answer = handle_code_review(user_input)
    else:
        answer = "Source: Agent system message\n\nUnsupported request type."

    print("\n===== FINAL ANSWER =====\n")
    print(answer)


if __name__ == "__main__":
    main()