import inspect
import logging

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from pyqt_utils.python.decorators import entryExitDec, exceptionDec, lessArgDec, timeDec

logger = logging.getLogger(__name__)
specialLogger = logging.getLogger(__name__ + '.special')


class TestClass:
    """
    Test decorators.

    Decorators use logger defined at module level
    with name 'logger' (if not provided explicitly).
    """

    @exceptionDec
    @entryExitDec
    @timeDec
    def foo(self):
        """Multiple decorators are allowed."""

    def bar(self):
        """Check decorators used directly as function call."""

    dec = timeDec(bar, specialLogger)
    bar = entryExitDec(exceptionDec(dec))

    @staticmethod
    @entryExitDec
    def baz():
        """Staticmethod decorator must be the last one."""

    @classmethod
    @entryExitDec
    def bazClass(cls):
        """Class-method decorator must be the last one."""

    @entryExitDec(logger=specialLogger)
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
    @entryExitDec
    def onSigIntStrRaw(self, num, text):
        pass

    @lessArgDec
    @entryExitDec
    def onSigIntStr(self, num, text):
        pass

    @staticmethod
    @entryExitDec
    def onSigIntStrRawStat(num, text):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDec
    def onSigIntStrStat(num, text):
        pass

    # limit to 1 arg
    @lessArgDec
    @entryExitDec
    def onSigInt(self, num):
        pass

    @entryExitDec
    @pyqtSlot(int)
    def onSigIntSlot(self, num):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDec
    def onSigIntStat(num):
        pass

    # limit to 0 arg
    @lessArgDec
    @entryExitDec
    def onSig(self):
        pass

    @entryExitDec
    @pyqtSlot()
    def onSigSlot(self):
        pass

    @staticmethod
    @lessArgDec
    @entryExitDec
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
