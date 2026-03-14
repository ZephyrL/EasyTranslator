from dataclasses import dataclass, field


@dataclass
class Paragraph:
    """A single paragraph extracted from a document."""
    index: int
    text: str


@dataclass
class Document:
    """A parsed document represented as a list of paragraphs."""
    file_path: str
    paragraphs: list[Paragraph] = field(default_factory=list)

    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)
