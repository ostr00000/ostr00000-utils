import inspect
import logging
import sys
import time
from functools import partial, wraps

from decorator import decorator as baseDecorator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from pyqt_utils.python.logger_skip_frame import SkipFrameInModule

SkipFrameInModule(__file__)
_moduleLogger = logging.getLogger(__name__)


def _lessArgAttempt(fun, *args, **kw):
    while True:
        try:
            return fun(*args, **kw)
        except TypeError as e:
            if e.args and 'positional argument' in e.args[0] and args:
                args = args[:-1]
            else:
                raise


_lessArgAttemptDec = baseDecorator(_lessArgAttempt, kwsyntax=True)


def decoratorForSlot(decoratorFun):
    """Fix for compatibility for decorator library >= 5.

    Wrap decorator to ignore TypeError when there is wrong number of parameters.
    Wrong number of parameters may be when there is missing `pyqtSlot` decorator.
    `pyqtSlot` should be used before any of these decorators.

    `pyqtSlot` may not work in the following example:
    >>>        import decorator
    >>>        from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject
    >>>
    >>>        @decorator.decorator
    >>>        def bazDec(fun, *args, **kwargs):
    >>>            return fun(*args, **kwargs)
    >>>
    >>>        class Foo(QObject):
    >>>            sig = pyqtSignal(str)
    >>>
    >>>            def __init__(self):
    >>>                super().__init__()
    >>>                self.sig.connect(self.bar)
    >>>
    >>>            @staticmethod
    >>>            @pyqtSlot()
    >>>            @bazDec
    >>>            def bar():
    >>>                print('ok')
    >>>
    >>>        foo = Foo()
    >>>        foo.sig.emit('isOk?')
    """
    dec = baseDecorator(decoratorFun, kwsyntax=True)  # decorator.decorate.fun

    def _decoratorForSlotInner(fun, *args, **kwargs):
        return dec(_lessArgAttemptDec(fun), *args, **kwargs)

    return _decoratorForSlotInner


def lessArgDec(fun):
    @wraps(fun)
    def _lessArgDecInner(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except TypeError:
            sig = inspect.signature(fun)
            args = args[: len(sig.parameters)]
            return fun(*args, **kwargs)

    return _lessArgDecInner


def _extractLogger(decObj):
    def _extractLoggerFunOrArg(decoratedFun=None, logger=None):
        nonlocal decObj
        if decoratedFun is None:
            if logger is None:
                msg = "Logger must be present in the decorated function"
                raise TypeError(msg)
            return partial(_extractLoggerFunOrArg, logger=logger)

        if not callable(decoratedFun):
            msg = "decoratedFun must be a function"
            raise TypeError(msg)

        if logger is None and (mod := sys.modules.get(decoratedFun.__module__, None)):
            logger = getattr(mod, 'logger', None)

        if logger:
            return decObj(decoratedFun, logger)
        return decObj(decoratedFun)

    return _extractLoggerFunOrArg


@_extractLogger
@decoratorForSlot
def exceptionDec(fun, logger=_moduleLogger, level=logging.ERROR, *args, **kwargs):
    try:
        return fun(*args, **kwargs)
    except Exception:
        logger.log(level, "Unknown exception", exc_info=True)
        raise


@_extractLogger
@decoratorForSlot
def entryExitDec(fun, logger=_moduleLogger, *args, **kwargs):
    logger.debug(f"Before: {fun.__name__}")
    result = fun(*args, **kwargs)
    logger.debug(f"After: {fun.__name__}")
    return result


@_extractLogger
@decoratorForSlot
def timeDec(fun, logger=_moduleLogger, *args, **kwargs):
    start = time.time()
    try:
        return fun(*args, **kwargs)
    finally:
        logger.debug(f"{fun.__name__}, execute time:{time.time() - start :.4f}s")


@decoratorForSlot
def cursorDec(fun, cursor=Qt.WaitCursor, *args, **kwargs):
    QApplication.setOverrideCursor(cursor)
    try:
        return fun(*args, **kwargs)
    finally:
        QApplication.restoreOverrideCursor()


@decoratorForSlot
def singleCallDec(
    fun, *args, attrName='__is_calling__', callingDefaultValue=None, **kwargs
):
    isCalling = getattr(fun, attrName, False)
    if isCalling:
        return callingDefaultValue
    setattr(fun, attrName, True)
    try:
        return fun(*args, **kwargs)
    finally:
        setattr(fun, attrName, False)
