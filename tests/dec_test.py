import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from pyqt_utils.python.decorators import (
    entryExitDecFactory,
    exceptionDecFactory,
    lessArgDec,
    timeDecFactory,
)

logger = logging.getLogger(__name__)
specialLogger = logging.getLogger(__name__ + '.special')


class TestClass:
    """
    Test decorators.

    Decorators use logger defined at module level
    with name 'logger' (if not provided explicitly).
    """

    @exceptionDecFactory()
    @entryExitDecFactory()
    @timeDecFactory()
    def foo(self):
        """Multiple decorators are allowed."""

    def bar(self):
        """Check decorators used directly as function call."""

    _d1 = timeDecFactory(logger=specialLogger)(bar)
    _d2 = exceptionDecFactory()(_d1)
    bar = entryExitDecFactory()(_d2)

    @staticmethod
    @entryExitDecFactory()
    def baz():
        """Staticmethod decorator must be the last one."""

    @classmethod
    @entryExitDecFactory()
    def bazClass(cls):
        """Class-method decorator must be the last one."""

    @entryExitDecFactory(logger=specialLogger)
    @lessArgDec
    def fooBar(self):
        """Check a function with custom logger."""


class TestSlotClass(QObject):
    sig = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.sig.connect(self.onSigIntStrRaw)
        self.sig.connect(self.onSigIntStr)
        self.sig.connect(self.onSigIntStrRawStat)
        self.sig.connect(self.onSigIntStrStat)

        self.sig.connect(self.onSigInt)
        self.sig.connect(self.onSigIntSlot)
        self.sig.connect(self.onSigIntStat)

        self.sig.connect(self.onSig)
        self.sig.connect(self.onSigSlot)
        self.sig.connect(self.onSigStat)

    def run(self):
        self.sig.emit(123, 'ok')

    # all arg possibilities
    @entryExitDecFactory()
    def onSigIntStrRaw(self, num, text):
        pass

    @lessArgDec
    @entryExitDecFactory()
    def onSigIntStr(self, num, text):
        pass

    @staticmethod
    @entryExitDecFactory()
    def onSigIntStrRawStat(num, text):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDecFactory()
    def onSigIntStrStat(num, text):
        pass

    # limit to 1 arg
    @lessArgDec
    @entryExitDecFactory()
    def onSigInt(self, num):
        pass

    @entryExitDecFactory()
    @pyqtSlot(int)
    def onSigIntSlot(self, num):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDecFactory()
    def onSigIntStat(num):
        pass

    # limit to 0 arg
    @lessArgDec
    @entryExitDecFactory()
    def onSig(self):
        pass

    @entryExitDecFactory()
    @pyqtSlot()
    def onSigSlot(self):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDecFactory()
    def onSigStat():
        pass


def runAllFunctions():
    testObj = TestClass()
    for fun in TestClass.__dict__.values():
        if inspect.isfunction(fun):
            fun(testObj)

    testSlotObj = TestSlotClass()
    testSlotObj.run()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(name)-20s: %(message)s',
    )
    runAllFunctions()
