def clean_text(text: str) -> str:
    """
    Basic cleanup:
    - normalize line endings
    - reduce excessive whitespace
    - preserve useful line structure
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines: list[str] = []
    previous_blank = False

    for line in text.split("\n"):
        cleaned_line = " ".join(line.split()).strip()

        if cleaned_line == "":
            if not previous_blank:
                lines.append("")
            previous_blank = True
        else:
            lines.append(cleaned_line)
            previous_blank = False

    return "\n".join(lines).strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping character-based chunks.
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap")

    cleaned = clean_text(text)

    if not cleaned:
        return []

    chunks: list[str] = []
    start = 0
    text_length = len(cleaned)

    while start < text_length:
        end = start + chunk_size
        chunk = cleaned[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start += chunk_size - overlap

    return chunks