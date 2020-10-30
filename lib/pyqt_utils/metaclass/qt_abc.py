from abc import ABCMeta

from PyQt5.QtCore import QObject

from pyqt_utils.metaclass.base import BaseMeta


class QtAbcMeta(BaseMeta, ABCMeta, type(QObject)):
    pass
