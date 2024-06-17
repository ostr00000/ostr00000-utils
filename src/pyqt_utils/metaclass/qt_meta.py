from abc import ABCMeta

from PyQt5.QtWidgets import QWidget

from pyqt_utils.metaclass.debug import ConflictHelperMeta, RemainingKwMeta
from typing import TYPE_CHECKING


if TYPE_CHECKING:

    class QtMeta(type):
        pass

else:
    QtMeta = type(QWidget)


class AbcQtMeta(ConflictHelperMeta, ABCMeta, QtMeta, RemainingKwMeta, type):
    pass
