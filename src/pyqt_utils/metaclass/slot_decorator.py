import types

from pyqt_utils.metaclass.qt_meta import AbcQtMeta
from pyqt_utils.python.decorators import entryExitDec, exceptionDec


class SlotDecoratorMeta(AbcQtMeta):
    def __new__(cls, name, bases, namespace, **kwargs):
        for funName, fun in namespace.items():
            if not isinstance(fun, types.FunctionType):
                continue

            if not fun.__name__.startswith('on'):
                continue

            namespace[funName] = exceptionDec(entryExitDec(fun))

        return super().__new__(cls, name, bases, namespace, **kwargs)
