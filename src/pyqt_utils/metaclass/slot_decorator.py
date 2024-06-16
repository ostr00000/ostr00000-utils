import types

from PyQt5.QtCore import QObject
from pyqt_utils.metaclass.base import BaseMeta
from pyqt_utils.python.decorators import entryExitDec, exceptionDec


class SlotDecoratorMeta(BaseMeta, type(QObject)):
    def __new__(mcs, name, bases, namespace):
        for funName, fun in namespace.items():
            if not isinstance(fun, types.FunctionType):
                continue

            if not fun.__name__.startswith('on'):
                continue

            namespace[funName] = exceptionDec(entryExitDec(fun))

        return super().__new__(mcs, name, bases, namespace)
