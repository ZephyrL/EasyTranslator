from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox

from src.models.parsers.registry import parse_document
from src.models.session import Session
from src.services.session_store import save_session, load_session
from src.views.launch_view import LaunchView
from src.views.translation_view import TranslationView


class App(QMainWindow):
    """Main application window managing navigation between views."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EasyTranslator")
        self.resize(1100, 700)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Views
        self._launch_view = LaunchView()
        self._translation_view = TranslationView()

        self._stack.addWidget(self._launch_view)
        self._stack.addWidget(self._translation_view)

        # Connections
        self._launch_view.open_document_requested.connect(self._open_document)
        self._launch_view.resume_session_requested.connect(self._resume_session)
        self._translation_view.back_requested.connect(self._show_launch)

        self._show_launch()

    def _show_launch(self):
        self._launch_view.refresh_sessions()
        self._stack.setCurrentWidget(self._launch_view)
        self.setWindowTitle("EasyTranslator")

    def _open_document(self, file_path: str):
        try:
            document = parse_document(file_path)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open document:\n{e}")
            return

        if document.paragraph_count == 0:
            QMessageBox.information(self, "Empty Document", "No paragraphs found in this document.")
            return

        session = Session.create_new(file_path, document.paragraph_count)
        save_session(session)
        self._load_translation_view(document, session)

    def _resume_session(self, session_id: str):
        session = load_session(session_id)
        if session is None:
            QMessageBox.warning(self, "Error", "Session not found.")
            return
        try:
            document = parse_document(session.document_path)
        except Exception as e:
            QMessageBox.warning(
                self, "Error",
                f"Cannot open the original document:\n{session.document_path}\n\n{e}"
            )
            return

        self._load_translation_view(document, session)

    def _load_translation_view(self, document, session):
        self._translation_view.load_session(document, session)
        self._stack.setCurrentWidget(self._translation_view)
        self.setWindowTitle(f"EasyTranslator — {session.document_name}")

    def keyPressEvent(self, event):
        """Global keyboard shortcuts."""
        if self._stack.currentWidget() is self._translation_view:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                    self._translation_view.handle_key_navigation(event.key())
                    return
        super().keyPressEvent(event)

    def closeEvent(self, event):
        """Save session on close."""
        self._translation_view.save_now()
        event.accept()
