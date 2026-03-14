import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from src.models.document import Document, Paragraph


def parse_epub(file_path: str) -> Document:
    """Parse an EPUB file: extract HTML chapters, strip tags, split into paragraphs."""
    book = epub.read_epub(file_path)
    paragraphs = []
    idx = 0

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        # Extract text from <p> tags for cleaner paragraph separation
        p_tags = soup.find_all("p")
        if p_tags:
            for p in p_tags:
                text = p.get_text(separator=" ").strip()
                if text:
                    paragraphs.append(Paragraph(index=idx, text=text))
                    idx += 1
        else:
            # Fallback: split full text by blank lines
            full_text = soup.get_text(separator="\n")
            for block in full_text.split("\n\n"):
                text = block.strip()
                if text:
                    paragraphs.append(Paragraph(index=idx, text=text))
                    idx += 1

    return Document(file_path=file_path, paragraphs=paragraphs)
