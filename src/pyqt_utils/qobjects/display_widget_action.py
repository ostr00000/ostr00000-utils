import logging
from abc import abstractmethod
from typing import Generic

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget

from pyqt_utils.metaclass.base import QtAbcMeta
from pyqt_utils.python.decorators import safeRun

logger = logging.getLogger(__name__)


class DisplayWidgetAction[W: QWidget](QAction, metaclass=QtAbcMeta):
    def __init__(self, icon=QIcon(), text='', parent: QWidget | None = None):
        super().__init__(icon, text, parent)
        self._widget: W | None = None
        self.triggered.connect(self.onTriggered)

    @property
    def widget(self) -> W:
        if self._widget is None:
            msg = (
                "Widget is not initialized. "
                "You may call `triggered` before this call."
            )
            raise TypeError(msg)
        return self._widget

    @safeRun
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
    def createWidget(self) -> W:
        raise NotImplementedError
