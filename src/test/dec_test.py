import inspect
import logging

from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot

from pyqt_utils.python.decorators import entryExitDec, timeDec, exceptionDec, lessArgDec

logger = logging.getLogger(__name__)
specialLogger = logging.getLogger(__name__ + '.special')


class TestClass:
    """
    Decorators use logger defined at module level
    with name 'logger' (if not provided explicitly).
    """

    @exceptionDec
    @entryExitDec
    @timeDec
    def foo(self):
        """Multiple decorators are allowed"""
        print('foo')

    def bar(self):
        """Decorators may be used directly as function call"""
        print('bar')

    dec = timeDec(bar, specialLogger)
    bar = entryExitDec(exceptionDec(dec))

    @staticmethod
    @entryExitDec
    def baz():
        """Staticmethod decorator must be the last one"""
        print('baz')

    @classmethod
    @entryExitDec
    def bazClass(cls):
        """Callmethod decorator must be the last one"""
        print('bazClass')

    @entryExitDec(logger=specialLogger)
    @lessArgDec
    def fooBar(self):
        """Custom logger may be provided"""
        print('fooBar')


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
        print(f'onSigIntStrRaw with {num=}, {text=}')

    @lessArgDec
    @entryExitDec
    def onSigIntStr(self, num, text):
        print(f'onSigIntStr with {num=}, {text=}')

    @staticmethod
    @entryExitDec
    def onSigIntStrRawStat(num, text):
        print(f'onSigIntStrRawStat with {num=}, {text=}')

    @staticmethod
    @lessArgDec
    @entryExitDec
    def onSigIntStrStat(num, text):
        print(f'onSigIntStrStat with {num=}, {text=}')

    # limit to 1 arg
    @lessArgDec
    @entryExitDec
    def onSigInt(self, num):
        print(f'onSigInt with {num=}')

    @entryExitDec
    @pyqtSlot(int)
    def onSigIntSlot(self, num):
        print(f'onSigIntSlot with {num=}')

    @staticmethod
    @lessArgDec
    @entryExitDec
    def onSigIntStat(num):
        print(f'onSigIntStat with {num=}')

    # limit to 0 arg
    @lessArgDec
    @entryExitDec
    def onSig(self):
        print(f'onSig')

    @entryExitDec
    @pyqtSlot()
    def onSigSlot(self):
        print(f'onSigSlot')

    @staticmethod
    @lessArgDec
    @entryExitDec
    def onSigStat():
        print(f'onSigStat')


def runAllFunctions():
    testObj = TestClass()
    for fun in TestClass.__dict__.values():
        if inspect.isfunction(fun):
            fun(testObj)

    testSlotObj = TestSlotClass()
    testSlotObj.run()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG, format='%(name)-20s: %(message)s', )
    runAllFunctions()
