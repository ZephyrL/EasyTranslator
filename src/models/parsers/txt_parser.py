from src.models.document import Document, Paragraph


def parse_txt(file_path: str) -> Document:
    """Parse a plain text file into paragraphs split by blank lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    raw_blocks = content.split("\n\n")
    paragraphs = []
    idx = 0
    for block in raw_blocks:
        text = block.strip()
        if text:
            paragraphs.append(Paragraph(index=idx, text=text))
            idx += 1

    return Document(file_path=file_path, paragraphs=paragraphs)
