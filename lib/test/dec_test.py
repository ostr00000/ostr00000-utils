import inspect
import logging

from pyqt_utils.python.common_decorators import actionDec, timeDec, exceptionDec

logger = logging.getLogger(__name__)
specialLogger = logging.getLogger(__name__ + '.special')


class TestClass:
    """Decorators use logger defined at module level with name 'logger'
    (if not provided explicite)
    """

    @exceptionDec
    @actionDec
    @timeDec
    def foo(self):
        """Multiple decorators are allowed"""
        print('foo')

    def bar(self):
        """Decorators may be used directly as function call"""
        print('bar')

    dec = timeDec(bar, specialLogger)
    bar = actionDec(exceptionDec(dec))

    @staticmethod
    @actionDec
    def baz():
        """Staticmethod decorator must be the last one"""
        print('baz')

    @classmethod
    @actionDec
    def bazClass(cls):
        """Callmethod decorator must be the last one"""
        print('bazClass')

    @actionDec(logger=specialLogger)
    def fooBar(self):
        """Custom logger may be provided"""
        print('fooBar')


def runAllFunctions():
    testObj = TestClass()
    for fun in TestClass.__dict__.values():
        if inspect.isfunction(fun):
            fun(testObj)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG, format='%(name)-20s: %(message)s', )
    runAllFunctions()
