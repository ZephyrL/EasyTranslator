from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QTextEdit, QLabel, QFrame, QHBoxLayout,
)


class _ParagraphEditor(QFrame):
    """A single paragraph's translation editor with its index label."""

    text_changed = Signal(int, str)  # (paragraph_index, new_text)
    focused = Signal(int)  # paragraph_index

    def __init__(self, index: int, parent=None):
        super().__init__(parent)
        self._index = index
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self._setup_ui()
        self._apply_style(False)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        header = QHBoxLayout()
        self._label = QLabel(f"§ {self._index + 1}")
        self._label.setStyleSheet("font-weight: bold; color: #666; font-size: 11px;")
        header.addWidget(self._label)
        header.addStretch()
        layout.addLayout(header)

        self._editor = QTextEdit()
        self._editor.setPlaceholderText("Type your translation here...")
        self._editor.setAcceptRichText(False)
        self._editor.setMinimumHeight(60)
        self._editor.setMaximumHeight(200)
        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.focusInEvent = self._wrap_focus_in(self._editor.focusInEvent)
        layout.addWidget(self._editor)

    def _wrap_focus_in(self, original):
        def handler(event):
            original(event)
            self.focused.emit(self._index)
        return handler

    def _on_text_changed(self):
        self.text_changed.emit(self._index, self._editor.toPlainText())

    def set_text(self, text: str):
        self._editor.blockSignals(True)
        self._editor.setPlainText(text)
        self._editor.blockSignals(False)

    def get_text(self) -> str:
        return self._editor.toPlainText()

    def set_highlighted(self, highlighted: bool):
        self._apply_style(highlighted)

    def focus_editor(self):
        self._editor.setFocus()

    def _apply_style(self, highlighted: bool):
        if highlighted:
            self.setStyleSheet(
                "_ParagraphEditor { background: #FFF9C4; border: 1px solid #F9A825; border-radius: 4px; }"
            )
        else:
            self.setStyleSheet(
                "_ParagraphEditor { background: #ffffff; border: 1px solid #ddd; border-radius: 4px; }"
            )


class EditorPanel(QWidget):
    """Right panel: per-paragraph translation editors."""

    translation_changed = Signal(int, str)  # (paragraph_index, text)
    paragraph_focused = Signal(int)  # paragraph_index

    def __init__(self, parent=None):
        super().__init__(parent)
        self._editors: list[_ParagraphEditor] = []
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

    def load_paragraphs(self, paragraph_count: int, translations: dict[int, str] | None = None):
        """Create one editor per paragraph, optionally pre-filled with saved translations."""
        for editor in self._editors:
            editor.deleteLater()
        self._editors.clear()

        for i in range(paragraph_count):
            editor = _ParagraphEditor(i)
            if translations and i in translations:
                editor.set_text(translations[i])
            editor.text_changed.connect(self._on_text_changed)
            editor.focused.connect(self._on_editor_focused)
            self._container_layout.addWidget(editor)
            self._editors.append(editor)

    def set_focus(self, index: int):
        """Highlight and scroll to the specified paragraph editor."""
        if index == self._focused_index:
            return
        if 0 <= self._focused_index < len(self._editors):
            self._editors[self._focused_index].set_highlighted(False)
        if 0 <= index < len(self._editors):
            self._editors[index].set_highlighted(True)
            self._scroll.ensureWidgetVisible(self._editors[index], 50, 50)
        self._focused_index = index

    def focus_editor_at(self, index: int):
        """Set focus to the text editor of a specific paragraph."""
        if 0 <= index < len(self._editors):
            self._editors[index].focus_editor()

    def get_translation(self, index: int) -> str:
        if 0 <= index < len(self._editors):
            return self._editors[index].get_text()
        return ""

    def get_all_translations(self) -> dict[int, str]:
        return {i: e.get_text() for i, e in enumerate(self._editors) if e.get_text().strip()}

    def _on_text_changed(self, index: int, text: str):
        self.translation_changed.emit(index, text)

    def _on_editor_focused(self, index: int):
        self.paragraph_focused.emit(index)
