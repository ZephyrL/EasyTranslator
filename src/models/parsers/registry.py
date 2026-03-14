from pathlib import Path

from src.models.document import Document
from src.models.parsers.txt_parser import parse_txt
from src.models.parsers.pdf_parser import parse_pdf
from src.models.parsers.docx_parser import parse_docx
from src.models.parsers.epub_parser import parse_epub

_PARSERS = {
    ".txt": parse_txt,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".epub": parse_epub,
}

SUPPORTED_EXTENSIONS = list(_PARSERS.keys())

FILE_FILTER = "Supported Documents ({});;All Files (*)".format(
    " ".join(f"*{ext}" for ext in SUPPORTED_EXTENSIONS)
)


def parse_document(file_path: str) -> Document:
    """Select the appropriate parser based on file extension and parse the document."""
    ext = Path(file_path).suffix.lower()
    parser = _PARSERS.get(ext)
    if parser is None:
        raise ValueError(f"Unsupported file format: {ext}")
    return parser(file_path)
