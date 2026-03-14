import fitz  # PyMuPDF

from src.models.document import Document, Paragraph


def parse_pdf(file_path: str) -> Document:
    """Extract text from a PDF and split into paragraphs."""
    doc = fitz.open(file_path)
    paragraphs = []
    idx = 0

    for page in doc:
        text = page.get_text("text")
        blocks = text.split("\n\n")
        for block in blocks:
            cleaned = block.strip()
            if cleaned:
                paragraphs.append(Paragraph(index=idx, text=cleaned))
                idx += 1

    doc.close()
    return Document(file_path=file_path, paragraphs=paragraphs)
