from functools import partial

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QValidator
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QWidget

_emptyWindowFlags = Qt.WindowFlags()


class SpaceLineEdit(QWidget):
    textChanged = pyqtSignal(str)

    def __init__(
        self,
        parent: QWidget = None,
        validator: QValidator = None,
        flags=_emptyWindowFlags,
        splitChars=' ,;',
        textSeparator=',',
    ):
        super().__init__(parent, flags)
        self.setFocusPolicy(Qt.StrongFocus)
        self._validator = validator
        self.splitChars = splitChars
        self.textSeparator = textSeparator

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
        widgets = [self._layout.itemAt(i).widget() for i in range(self._layout.count())]

        for w in widgets:
            if w and w not in self._lineEdits:
                self._layout.removeWidget(w)
                w.deleteLater()

        for i, le in enumerate(self._lineEdits):
            if le not in widgets:
                self._layout.insertWidget(i, le)

    def setValidator(self, validator: QValidator):
        self._validator = validator

    def text(self):
        return self.textSeparator.join(self.getValues())

    def getValues(self) -> list[str]:
        return [le.text() for le in self._lineEdits]

    def setText(self, text: str):
        self.setValues(self._splitText(text))

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

        match self._splitText(text):
            case [str(first), *others]:
                lineEdit.setText(first)
                insertIndex = self._lineEdits.index(lineEdit) + 1
                for index, text in enumerate(others, insertIndex):
                    self._lineEdits.insert(index, self._createLineEdit(text))
                self._refreshLayout()
                self._setFocus(lineEdit, offset=1)

        self._isUpdating = False
        self.textChanged.emit(self.text())

    def _splitText(self, text: str) -> list[str]:
        for sch in self.splitChars[1:]:
            text = text.replace(sch, self.splitChars[0])

        return text.split(self.splitChars[0])

    def _removeLineEdit(self, lineEdit: QLineEdit, *, changeFocus=True):
        if len(self._lineEdits) <= 1:  # there must be always at least one line edit
            return

        if changeFocus and not self._setFocus(lineEdit, offset=-1):
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
