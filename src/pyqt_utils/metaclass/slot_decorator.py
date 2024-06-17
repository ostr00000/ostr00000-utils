import types

from pyqt_utils.metaclass.qt_meta import AbcQtMeta
from pyqt_utils.python.decorators import entryExitDecFactory, exceptionDecFactory


class SlotDecoratorMeta(AbcQtMeta):
    def __new__(cls, name, bases, namespace, **kwargs):
        for funName, fun in namespace.items():
            if not isinstance(fun, types.FunctionType):
                continue

            if not fun.__name__.startswith('on'):
                continue

            f1 = exceptionDecFactory()
            f2 = entryExitDecFactory()
            namespace[funName] = f1(f2(fun))

        return super().__new__(cls, name, bases, namespace, **kwargs)
