from abc import ABCMeta

from PyQt5.QtWidgets import QWidget

from pyqt_utils.metaclass.debug import ConflictHelperMeta, RemainingKwMeta

QtMeta: type = type(QWidget)


class AbcQtMeta(ConflictHelperMeta, ABCMeta, QtMeta, RemainingKwMeta, type):
    pass
