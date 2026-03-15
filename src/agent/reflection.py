from src.config import MIN_KB_SCORE, MIN_MODEL_KNOWLEDGE_CONFIDENCE


def best_kb_score(retrieved_chunks: list[dict]) -> float:
    if not retrieved_chunks:
        return 0.0
    return float(retrieved_chunks[0]["score"])


def is_kb_strong_enough(retrieved_chunks: list[dict]) -> bool:
    return best_kb_score(retrieved_chunks) >= MIN_KB_SCORE


def extract_model_confidence(answer_text: str) -> float:
    """
    Extract confidence value from the last 'Confidence:' line if present.
    """
    lines = [line.strip() for line in answer_text.splitlines() if line.strip()]

    for line in reversed(lines):
        if line.startswith("Confidence:"):
            raw_value = line.replace("Confidence:", "").strip()
            try:
                return float(raw_value)
            except ValueError:
                return 0.0

    return 0.0


def is_model_knowledge_strong_enough(answer_text: str) -> bool:
    confidence = extract_model_confidence(answer_text)
    return confidence >= MIN_MODEL_KNOWLEDGE_CONFIDENCE


def remove_confidence_line(answer_text: str) -> str:
    lines = answer_text.splitlines()
    filtered = [line for line in lines if not line.strip().startswith("Confidence:")]
    return "\n".join(filtered).strip()


def ensure_general_knowledge_label(answer_text: str) -> str:
    cleaned = remove_confidence_line(answer_text)

    if cleaned.startswith("Source: General model knowledge"):
        return cleaned

    return f"Source: General model knowledge\n\n{cleaned}"