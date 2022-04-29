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
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._prepareLineEdit(0)

    def setValidator(self, validator: QValidator):
        self._validator = validator

    def getValues(self) -> list[str]:
        values = []
        for index in range(self._layout.count()):
            text = self._layout.itemAt(index).widget().text()
            values.append(text)
        return values

    def setValues(self, values: list[str]):
        self._cleanAll()
        if not values:
            values = ['']
        for index, value in enumerate(values):
            self._prepareLineEdit(index, value)

    def _cleanAll(self):
        for index in reversed(range(self._layout.count())):
            widget = self._layout.takeAt(index).widget()
            widget.setParent(None)
            widget.deleteLater()

    def _prepareLineEdit(self, position: int, text=''):
        lineEdit = QLineEdit(str(text), self)
        lineEdit.setValidator(self._validator)
        lineEdit.textChanged.connect(partial(self.onTextChanged, lineEdit))
        lineEdit.installEventFilter(self)
        self._layout.insertWidget(position, lineEdit)

    def focusInEvent(self, event):
        item = self._layout.itemAt(0)
        if item:
            item.widget().setFocus()

    def onTextChanged(self, lineEdit: QLineEdit, text: str):
        if not text:
            self._removeLineEdit(lineEdit)

        text = self._convert(text)
        if self._isSplit(text):
            self._addLineEdit(lineEdit, text)

    def _removeLineEdit(self, lineEdit: QLineEdit, changeFocus=True):
        if self._layout.count() <= 1:
            return

        if changeFocus:
            if not self._setFocus(lineEdit, offset=-1):
                self._setFocus(lineEdit, offset=1)

        self._layout.removeWidget(lineEdit)
        lineEdit.deleteLater()

    @staticmethod
    def _convert(text: str) -> str:
        for sch in SpaceLineEdit.SPLIT_CHARS[1:]:
            text = text.replace(sch, ' ')
        return text

    @staticmethod
    def _isSplit(text: str) -> bool:
        return ' ' in text

    def _addLineEdit(self, lineEdit: QLineEdit, text: str):
        texts = text.split()
        if not texts:
            lineEdit.setText('')
            return
        else:
            lineEdit.setText(texts[0])

        if len(texts) == 1:
            texts.append('')

        insertIndex = self._layout.indexOf(lineEdit) + 1
        for index, text in enumerate(texts[1:], insertIndex):
            self._prepareLineEdit(index, text)

        self._setFocus(lineEdit, offset=1)

    def eventFilter(self, watched: QWidget, event: QEvent) -> bool:
        if isinstance(watched, QLineEdit):
            lineEdit = watched

            if event.type() == QEvent.FocusOut and not lineEdit.text():
                self._removeLineEdit(lineEdit, changeFocus=False)

            elif event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
                if event.key() == Qt.Key_Backspace and not lineEdit.text():
                    self._removeLineEdit(lineEdit)

                if event.key() == Qt.Key_Down:
                    self._setFocus(lineEdit, offset=1)
                elif event.key() == Qt.Key_Up:
                    self._setFocus(lineEdit, offset=-1)

        return super().eventFilter(watched, event)

    def _setFocus(self, lineEdit: QLineEdit, offset: int) -> bool:
        index = self._layout.indexOf(lineEdit) + offset
        item = self._layout.itemAt(index)
        if item:
            item.widget().setFocus(Qt.OtherFocusReason)
            return True

        return False
