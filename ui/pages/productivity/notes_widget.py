from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QSplitter, QSizePolicy,
)

from database.models import Note
from database.repositories.productivity_repository import ProductivityRepository


class NotesWidget(QWidget):
    """Notes sub-view with a note list on the left and an editor on the right."""

    def __init__(self, repo: ProductivityRepository, parent=None):
        super().__init__(parent)
        self._repo = repo
        self._selected_note: Note | None = None
        self._build()
        self.refresh()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(0, 0, 0, 10)
        toolbar.setSpacing(8)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Search notes…")
        self._search.setProperty("class", "search-input")
        self._search.textChanged.connect(self._on_search)

        self.add_btn = QPushButton("＋  New Note")
        self.add_btn.setProperty("class", "primary-btn")
        self.add_btn.clicked.connect(self._new_note)

        toolbar.addWidget(self._search, 1)
        toolbar.addWidget(self.add_btn)
        layout.addLayout(toolbar)

        # Splitter: left list | right editor
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left: Note list
        self._list = QListWidget()
        self._list.setProperty("class", "note-list")
        self._list.currentItemChanged.connect(self._on_note_selected)
        splitter.addWidget(self._list)

        # Right: Editor panel
        editor_panel = QWidget()
        editor_panel.setProperty("class", "note-editor-panel")
        ep_layout = QVBoxLayout(editor_panel)
        ep_layout.setContentsMargins(16, 0, 0, 0)
        ep_layout.setSpacing(8)

        self._editor_title = QLineEdit()
        self._editor_title.setPlaceholderText("Note title…")
        self._editor_title.setProperty("class", "note-title-input")

        self._editor_body = QTextEdit()
        self._editor_body.setPlaceholderText("Start writing your note here…")
        self._editor_body.setProperty("class", "note-body-editor")

        save_row = QHBoxLayout()
        save_row.addStretch()
        self.save_btn = QPushButton("💾  Save")
        self.save_btn.setProperty("class", "primary-btn")
        self.save_btn.clicked.connect(self._save_note)

        self.del_btn = QPushButton("🗑  Delete")
        self.del_btn.setProperty("class", "danger-btn")
        self.del_btn.clicked.connect(self._delete_note)
        self.del_btn.setVisible(False)

        save_row.addWidget(self.del_btn)
        save_row.addWidget(self.save_btn)

        ep_layout.addWidget(self._editor_title)
        ep_layout.addWidget(self._editor_body, 1)
        ep_layout.addLayout(save_row)
        splitter.addWidget(editor_panel)

        splitter.setSizes([260, 700])
        layout.addWidget(splitter, 1)

    # ── Helpers ──────────────────────────────────────────────────────────────

    def refresh(self, query: str = ""):
        self._list.clear()
        notes = self._repo.get_all_notes()
        if query:
            notes = [n for n in notes if query.lower() in n.title.lower()]

        for note in notes:
            item = QListWidgetItem(note.title or "Untitled")
            item.setData(Qt.ItemDataRole.UserRole, note)
            self._list.addItem(item)

    def _on_search(self, text: str):
        self.refresh(query=text)

    def _on_note_selected(self, current: QListWidgetItem, _previous):
        if current is None:
            return
        note: Note = current.data(Qt.ItemDataRole.UserRole)
        self._selected_note = note
        self._editor_title.setText(note.title or "")
        self._editor_body.setPlainText(note.content or "")
        self.del_btn.setVisible(True)

    def _new_note(self):
        self._selected_note = None
        self._editor_title.clear()
        self._editor_body.clear()
        self._editor_title.setFocus()
        self.del_btn.setVisible(False)
        self._list.clearSelection()

    def _save_note(self):
        title = self._editor_title.text().strip() or "Untitled"
        content = self._editor_body.toPlainText()

        if self._selected_note and self._selected_note.id:
            self._selected_note.title = title
            self._selected_note.content = content
            self._repo.update_note(self._selected_note)
        else:
            new_note = Note(title=title, content=content)
            saved = self._repo.add_note(new_note)
            self._selected_note = saved
        self.refresh(self._search.text())

    def _delete_note(self):
        if self._selected_note and self._selected_note.id:
            self._repo.delete_note(self._selected_note.id)
            self._selected_note = None
            self._editor_title.clear()
            self._editor_body.clear()
            self.del_btn.setVisible(False)
        self.refresh(self._search.text())
