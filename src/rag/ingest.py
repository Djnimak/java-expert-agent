from pathlib import Path

from src.loaders.pdf_loader import load_all_pdfs
from src.loaders.docx_loader import load_all_docx
from src.rag.chunking import chunk_text


def load_all_documents(project_root: Path) -> list[dict]:
    """
    Load all supported source documents into one unified list.
    """
    pdf_folder = project_root / "data" / "pdfs"
    docx_folder = project_root / "data" / "docx"

    pdf_documents = load_all_pdfs(pdf_folder)
    docx_documents = load_all_docx(docx_folder)

    unified_documents: list[dict] = []

    for file_name, text in pdf_documents.items():
        unified_documents.append(
            {
                "source_type": "pdf",
                "file_name": file_name,
                "text": text,
            }
        )

    for file_name, text in docx_documents.items():
        unified_documents.append(
            {
                "source_type": "docx",
                "file_name": file_name,
                "text": text,
            }
        )

    return unified_documents


def build_chunk_records(
    documents: list[dict],
    chunk_size: int = 1000,
    overlap: int = 200,
) -> list[dict]:
    """
    Convert documents into chunk records with metadata.
    """
    chunk_records: list[dict] = []

    for document in documents:
        chunks = chunk_text(
            text=document["text"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, chunk in enumerate(chunks):
            chunk_records.append(
                {
                    "source_type": document["source_type"],
                    "file_name": document["file_name"],
                    "chunk_index": chunk_index,
                    "text": chunk,
                }
            )

    return chunk_records