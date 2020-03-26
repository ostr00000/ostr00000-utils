import types

from PyQt5.QtCore import QObject

from pyqt_utils.python.common_decorators import exceptionDec, actionDec


class SlotDecorator(type(QObject), type):
    def __new__(mcs, name, bases, namespace):
        for funName, fun in namespace.items():
            if isinstance(fun, types.FunctionType):
                if fun.__name__.startswith('on'):
                    namespace[funName] = exceptionDec(actionDec(fun))

        return super().__new__(mcs, name, bases, namespace)
