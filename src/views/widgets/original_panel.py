from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QLabel, QFrame


class OriginalPanel(QWidget):
    """Left panel: displays original document paragraphs with focus highlighting."""

    paragraph_clicked = Signal(int)  # emits paragraph index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._paragraph_labels: list[QLabel] = []
        self._focused_index = -1
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._container_layout.setSpacing(4)
        self._container_layout.setContentsMargins(8, 8, 8, 8)

        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

    def load_paragraphs(self, paragraphs: list):
        """Populate the panel with paragraph text blocks."""
        # Clear existing
        for lbl in self._paragraph_labels:
            lbl.deleteLater()
        self._paragraph_labels.clear()

        for para in paragraphs:
            lbl = QLabel(para.text)
            lbl.setWordWrap(True)
            lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            lbl.setFrameShape(QFrame.Shape.StyledPanel)
            lbl.setStyleSheet(
                "QLabel { padding: 8px; background: #ffffff; border: 1px solid #ddd; border-radius: 4px; }"
            )
            lbl.setCursor(Qt.CursorShape.PointingHandCursor)
            # Click handler via mousePressEvent override
            idx = para.index
            lbl.mousePressEvent = lambda event, i=idx: self._on_click(i)
            self._container_layout.addWidget(lbl)
            self._paragraph_labels.append(lbl)

    def set_focus(self, index: int):
        """Highlight the focused paragraph and scroll to it."""
        if index == self._focused_index:
            return
        # Remove old highlight
        if 0 <= self._focused_index < len(self._paragraph_labels):
            self._paragraph_labels[self._focused_index].setStyleSheet(
                "QLabel { padding: 8px; background: #ffffff; border: 1px solid #ddd; border-radius: 4px; }"
            )
        # Apply new highlight
        if 0 <= index < len(self._paragraph_labels):
            self._paragraph_labels[index].setStyleSheet(
                "QLabel { padding: 8px; background: #FFF9C4; border: 1px solid #F9A825; border-radius: 4px; }"
            )
            self._scroll.ensureWidgetVisible(self._paragraph_labels[index], 50, 50)

        self._focused_index = index

    def _on_click(self, index: int):
        self.paragraph_clicked.emit(index)
