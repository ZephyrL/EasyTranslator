from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QPushButton,
    QLabel, QToolBar, QFileDialog, QMessageBox, QSizePolicy,
)

from src.models.document import Document
from src.models.session import Session
from src.views.widgets.original_panel import OriginalPanel
from src.views.widgets.editor_panel import EditorPanel
from src.services.session_store import save_session


class TranslationView(QWidget):
    """Main translation interface: horizontal split with original and editor panels."""

    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._document: Document | None = None
        self._session: Session | None = None
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(1000)
        self._save_timer.timeout.connect(self._auto_save)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet(
            "QToolBar { background: #f5f5f5; border-bottom: 1px solid #ddd; padding: 4px; spacing: 6px; }"
        )

        self._back_btn = QPushButton("← Home")
        self._back_btn.setStyleSheet("font-size: 12px; padding: 4px 12px;")
        self._back_btn.clicked.connect(self._on_back)
        toolbar.addWidget(self._back_btn)

        self._title_label = QLabel("")
        self._title_label.setStyleSheet("font-size: 13px; font-weight: bold; margin-left: 10px;")
        toolbar.addWidget(self._title_label)

        spacer = QWidget()
        spacer.setFixedWidth(20)
        toolbar.addWidget(spacer)

        self._progress_label = QLabel("")
        self._progress_label.setStyleSheet("font-size: 12px; color: #666;")
        toolbar.addWidget(self._progress_label)

        # Stretch spacer in toolbar
        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(stretch)

        self._export_btn = QPushButton("Export")
        self._export_btn.setStyleSheet("font-size: 12px; padding: 4px 12px;")
        self._export_btn.clicked.connect(self._on_export)
        toolbar.addWidget(self._export_btn)

        layout.addWidget(toolbar)

        # Splitter
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        self._original_panel = OriginalPanel()
        self._editor_panel = EditorPanel()

        self._splitter.addWidget(self._original_panel)
        self._splitter.addWidget(self._editor_panel)
        self._splitter.setSizes([500, 500])

        layout.addWidget(self._splitter, stretch=1)

        # Connect signals
        self._original_panel.paragraph_clicked.connect(self._on_paragraph_focus)
        self._editor_panel.paragraph_focused.connect(self._on_paragraph_focus)
        self._editor_panel.translation_changed.connect(self._on_translation_changed)

    def load_session(self, document: Document, session: Session):
        """Load a document and session into the view."""
        self._document = document
        self._session = session

        self._title_label.setText(session.document_name)
        self._original_panel.load_paragraphs(document.paragraphs)
        self._editor_panel.load_paragraphs(
            document.paragraph_count, session.translations
        )
        self._update_progress()

        # Restore focused paragraph
        if session.focused_index < document.paragraph_count:
            self._on_paragraph_focus(session.focused_index)

    def _on_paragraph_focus(self, index: int):
        """Synchronize focus between both panels."""
        self._original_panel.set_focus(index)
        self._editor_panel.set_focus(index)
        if self._session:
            self._session.focused_index = index
            self._schedule_save()

    def _on_translation_changed(self, index: int, text: str):
        """Handle text changes in the editor."""
        if self._session:
            if text.strip():
                self._session.translations[index] = text
            else:
                self._session.translations.pop(index, None)
            self._update_progress()
            self._schedule_save()

    def _update_progress(self):
        if self._session:
            done = self._session.translated_count
            total = self._session.paragraph_count
            self._progress_label.setText(f"{done}/{total} paragraphs translated")

    def _schedule_save(self):
        """Debounced auto-save: restart the 1-second timer on each change."""
        self._save_timer.start()

    def _auto_save(self):
        if self._session:
            save_session(self._session)

    def save_now(self):
        """Immediate save (for app close)."""
        self._save_timer.stop()
        if self._session:
            save_session(self._session)

    def _on_back(self):
        self.save_now()
        self.back_requested.emit()

    def _on_export(self):
        if not self._document or not self._session:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Translation", f"{self._session.document_name}_translated.txt",
            "Text Files (*.txt)"
        )
        if not file_path:
            return
        lines = []
        for para in self._document.paragraphs:
            translation = self._session.translations.get(para.index, "")
            lines.append(f"[Original §{para.index + 1}]")
            lines.append(para.text)
            lines.append(f"[Translation §{para.index + 1}]")
            lines.append(translation if translation else "(not translated)")
            lines.append("")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        QMessageBox.information(self, "Export", f"Translation exported to:\n{file_path}")

    def handle_key_navigation(self, key):
        """Navigate paragraphs with keyboard shortcuts."""
        if not self._session:
            return
        idx = self._session.focused_index
        if key == Qt.Key.Key_Down:
            new_idx = min(idx + 1, self._session.paragraph_count - 1)
        elif key == Qt.Key.Key_Up:
            new_idx = max(idx - 1, 0)
        else:
            return
        self._on_paragraph_focus(new_idx)
        self._editor_panel.focus_editor_at(new_idx)
