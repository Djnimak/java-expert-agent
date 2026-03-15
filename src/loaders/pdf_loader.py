from pathlib import Path
import fitz  # PyMuPDF


def format_pdf_table(table_data: list[list[str]], table_index: int, page_number: int) -> str:
    """
    Convert extracted PDF table data into a readable text block for RAG.
    """
    lines: list[str] = [f"[TABLE {table_index} ON PAGE {page_number}]"]

    for row_index, row in enumerate(table_data, start=1):
        cleaned_cells: list[str] = []

        for cell in row:
            if cell is None:
                cleaned_cells.append("<empty>")
            else:
                cleaned_text = " ".join(str(cell).split()).strip()
                cleaned_cells.append(cleaned_text if cleaned_text else "<empty>")

        lines.append(f"Row {row_index}: " + " | ".join(cleaned_cells))

    return "\n".join(lines)


def extract_tables_from_pdf_page(page, page_number: int) -> list[str]:
    """
    Detect and extract tables from a PDF page using PyMuPDF.
    """
    table_texts: list[str] = []

    try:
        tables = page.find_tables()

        if tables and tables.tables:
            for table_index, table in enumerate(tables.tables, start=1):
                extracted = table.extract()
                if extracted:
                    table_texts.append(
                        format_pdf_table(extracted, table_index, page_number)
                    )
    except Exception as exc:
        print(f"Warning: table extraction failed on page {page_number}: {exc}")

    return table_texts


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text and detected tables from a PDF file using PyMuPDF.
    """
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    all_page_parts: list[str] = []

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            page_number = page_index + 1
            page = doc.load_page(page_index)

            page_parts: list[str] = [f"--- Page {page_number} ---"]

            # Normal page text
            raw_text = page.get_text("text", sort=True)
            page_text = " ".join(str(raw_text).split()).strip()
            if page_text:
                page_parts.append(page_text)

            # Tables
            table_texts = extract_tables_from_pdf_page(page, page_number)
            page_parts.extend(table_texts)

            all_page_parts.append("\n".join(page_parts))

    return "\n\n".join(all_page_parts).strip()


def load_all_pdfs(pdf_folder: Path) -> dict[str, str]:
    """
    Load all PDFs from a folder.
    Returns dictionary: {filename: extracted_text}
    """
    if not pdf_folder.exists():
        raise FileNotFoundError(f"PDF folder not found: {pdf_folder}")

    pdf_texts: dict[str, str] = {}

    for pdf_file in sorted(pdf_folder.glob("*.pdf")):
        print(f"Loading PDF: {pdf_file.name}")
        pdf_texts[pdf_file.name] = extract_text_from_pdf(pdf_file)

    return pdf_texts