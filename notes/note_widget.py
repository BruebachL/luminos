from PyQt5.QtWidgets import QTextEdit


class NoteWidget(QTextEdit):
    def __init__(self, parent, note):
        super().__init__(parent)
        self.parent = parent
        self.note = note
        self.setText(note.content)
        self.textChanged.connect(self.update_note_content)

    def update_note_content(self):
        self.note.content = self.document().toPlainText()