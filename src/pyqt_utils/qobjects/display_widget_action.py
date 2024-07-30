import logging
from abc import abstractmethod

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget

from pyqt_utils.metaclass.qt_meta import AbcQtMeta
from pyqt_utils.python.decorators import exceptionDecFactory

logger = logging.getLogger(__name__)
_emptyIcon = QIcon()


class DisplayWidgetAction[W: QWidget](QAction, metaclass=AbcQtMeta):
    def __init__(self, icon=_emptyIcon, text='', parent: QWidget | None = None):
        super().__init__(icon, text, parent)
        self._widget: W | None = None
        self.triggered.connect(self.onTriggered)

    def parent(self) -> QWidget | None:
        match super().parent():
            case (QWidget() | None) as p:
                return p
            case _:
                raise TypeError

    @property
    def widget(self) -> W:
        if self._widget is None:
            msg = (
                "Widget is not initialized. "
                "You may call `triggered` before this call."
            )
            raise TypeError(msg)
        return self._widget

    @exceptionDecFactory()
    def onTriggered(self):
        if self._widget is None:
            self._widget = self.createWidget()
            self._widget.destroyed.connect(self.onDestroyed)
            self._widget.setAttribute(Qt.WA_DeleteOnClose)
            self._widget.show()
        else:
            self._widget.raise_()

    def onDestroyed(self):
        self._widget = None

    @abstractmethod
    def createWidget(self, parent: QWidget | None = None) -> W:
        raise NotImplementedError
