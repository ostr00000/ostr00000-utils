import logging
from abc import abstractmethod
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QWidget

from pyqt_utils.metaclass.qt_abc import QtAbcMeta
from pyqt_utils.python.decorators import safeRun

logger = logging.getLogger(__name__)


class DisplayWidgetAction(QAction, metaclass=QtAbcMeta):
    def __init__(self, icon=QIcon(), text='', parent: QWidget = None):
        super().__init__(icon, text, parent)
        self.widget: Optional[QWidget] = None
        self.triggered.connect(self.onTriggered)

    @safeRun
    def onTriggered(self):
        if self.widget is None:
            self.widget = self.createWidget()
            self.widget.destroyed.connect(self.onDestroyed)
            self.widget.setAttribute(Qt.WA_DeleteOnClose)
            self.widget.show()
        else:
            self.widget.raise_()

    def onDestroyed(self):
        self.widget = None

    @abstractmethod
    def createWidget(self) -> QWidget:
        raise NotImplementedError
