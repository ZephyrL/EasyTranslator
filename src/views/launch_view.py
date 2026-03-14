import time
from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox,
)

from src.models.parsers.registry import FILE_FILTER
from src.services.session_store import list_sessions, delete_session


class LaunchView(QWidget):
    """First screen: open a document or resume a recent session."""

    open_document_requested = Signal(str)  # file_path
    resume_session_requested = Signal(str)  # session_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("EasyTranslator")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #333; margin-bottom: 4px;")
        layout.addWidget(title)

        subtitle = QLabel("A simple translation workspace for your beloved documents")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #888; margin-bottom: 20px;")
        layout.addWidget(subtitle)

        # Open Document button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._open_btn = QPushButton("  Open Document  ")
        self._open_btn.setStyleSheet(
            "QPushButton { font-size: 15px; padding: 10px 28px; background: #1976D2; "
            "color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: #1565C0; }"
        )
        self._open_btn.clicked.connect(self._on_open_document)
        btn_layout.addWidget(self._open_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addSpacing(20)

        # Recent sessions
        recent_label = QLabel("Recent Sessions")
        recent_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(recent_label)

        self._session_list = QListWidget()
        self._session_list.setStyleSheet(
            "QListWidget { border: 1px solid #ddd; border-radius: 4px; }"
            "QListWidget::item { padding: 8px; }"
            "QListWidget::item:selected { background: #E3F2FD; color: #333; }"
        )
        self._session_list.itemDoubleClicked.connect(self._on_session_double_clicked)
        layout.addWidget(self._session_list, stretch=1)

        # Delete session button
        bottom_bar = QHBoxLayout()
        self._delete_btn = QPushButton("Delete Selected")
        self._delete_btn.setStyleSheet("font-size: 12px; color: #c62828;")
        self._delete_btn.clicked.connect(self._on_delete_session)
        bottom_bar.addWidget(self._delete_btn)
        bottom_bar.addStretch()
        layout.addLayout(bottom_bar)

    def refresh_sessions(self):
        """Reload the recent sessions list from disk."""
        self._session_list.clear()
        sessions = list_sessions()
        for session in sessions:
            updated = datetime.fromtimestamp(session.updated_at).strftime("%Y-%m-%d %H:%M")
            progress = f"{session.translated_count}/{session.paragraph_count}"
            text = f"{session.document_name}  —  {progress} paragraphs  —  {updated}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, session.session_id)
            self._session_list.addItem(item)

    def _on_open_document(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Document", "", FILE_FILTER
        )
        if file_path:
            self.open_document_requested.emit(file_path)

    def _on_session_double_clicked(self, item: QListWidgetItem):
        session_id = item.data(Qt.ItemDataRole.UserRole)
        if session_id:
            self.resume_session_requested.emit(session_id)

    def _on_delete_session(self):
        item = self._session_list.currentItem()
        if not item:
            return
        session_id = item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self, "Delete Session",
            f"Delete this session permanently?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            delete_session(session_id)
            self.refresh_sessions()
