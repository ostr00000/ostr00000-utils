from functools import partial

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QValidator, QKeyEvent
from PyQt5.QtWidgets import QLineEdit, QHBoxLayout, QWidget


class SpaceLineEdit(QWidget):
    SPLIT_CHARS = ' ,;'

    def __init__(self, parent: QWidget = None,
                 validator: QValidator = None,
                 flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setFocusPolicy(Qt.StrongFocus)
        self._validator = validator
        self._lineEdits: list[QLineEdit] = [self._createLineEdit()]
        self._isUpdating = False
        self._initStartWidget()
        self._refreshLayout()

    def _initStartWidget(self):
        self._layout = self._createLayout()
        self.setLayout(self._layout)

    @staticmethod
    def _createLayout():
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        return layout

    def _refreshLayout(self):
        widgets = [self._layout.itemAt(i).widget()
                   for i in range(self._layout.count())]

        for w in widgets:
            if w and w not in self._lineEdits:
                self._layout.removeWidget(w)
                w.deleteLater()

        for i, le in enumerate(self._lineEdits):
            if le not in widgets:
                self._layout.insertWidget(i, le)

    def setValidator(self, validator: QValidator):
        self._validator = validator

    def getValues(self) -> list[str]:
        return [le.text() for le in self._lineEdits]

    def setValues(self, values: list[str]):
        if not values:
            values = ['']

        self._lineEdits.clear()
        self._lineEdits = [self._createLineEdit(val) for val in values]
        self._refreshLayout()

    def _createLineEdit(self, text=''):
        lineEdit = QLineEdit(str(text), self)
        lineEdit.setValidator(self._validator)
        lineEdit.textChanged.connect(partial(self.onTextChanged, lineEdit))
        lineEdit.installEventFilter(self)
        return lineEdit

    def focusInEvent(self, event):
        layout = self.layout()
        while layout:
            item = layout.itemAt(0)
            if not item:
                return

            widget = item.widget()
            if widget:
                widget.setFocus()
                return

            layout = item.layout()

    def onTextChanged(self, lineEdit: QLineEdit, text: str):
        if self._isUpdating:
            return
        self._isUpdating = True

        text = self._convert(text)
        if self.SPLIT_CHARS[0] in text:
            texts = text.split(self.SPLIT_CHARS[0]) or ['']
            lineEdit.setText(texts[0])
            if texts != ['', '']:
                insertIndex = self._lineEdits.index(lineEdit) + 1
                for index, text in enumerate(texts[1:], insertIndex):
                    self._lineEdits.insert(index, self._createLineEdit(text))
                self._refreshLayout()
                self._setFocus(lineEdit, offset=1)

        self._isUpdating = False

    @classmethod
    def _convert(cls, text: str) -> str:
        for sch in cls.SPLIT_CHARS[1:]:
            text = text.replace(sch, cls.SPLIT_CHARS[0])
        return text

    def _removeLineEdit(self, lineEdit: QLineEdit, changeFocus=True):
        if len(self._lineEdits) <= 1:  # there must be always at least one line edit
            return

        if changeFocus:
            if not self._setFocus(lineEdit, offset=-1):
                self._setFocus(lineEdit, offset=1)

        try:
            self._lineEdits.remove(lineEdit)
            self._refreshLayout()
        except ValueError:
            pass  # we may call this function 2 times: FocusOut event or onTextChanged

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:
        if isinstance(watched, QLineEdit):
            lineEdit = watched

            if event.type() == QEvent.FocusOut and not lineEdit.text():
                self._removeLineEdit(lineEdit, changeFocus=False)

            elif event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
                if event.key() == Qt.Key_Backspace and not lineEdit.text():
                    self._removeLineEdit(lineEdit)
                elif event.key() == Qt.Key_Down:
                    self._setFocus(lineEdit, offset=1)
                elif event.key() == Qt.Key_Up:
                    self._setFocus(lineEdit, offset=-1)

        return super().eventFilter(watched, event)

    def _setFocus(self, lineEdit: QLineEdit, offset: int) -> bool:
        index = self._lineEdits.index(lineEdit) + offset
        if 0 <= index < len(self._lineEdits):
            self._lineEdits[index].setFocus(Qt.OtherFocusReason)
            return True
        return False
