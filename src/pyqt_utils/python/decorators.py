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


_lessArgAttemptDec = baseDecorator(_lessArgAttempt, kwsyntax=True)  # type: ignore[reportCallIssue]


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
    dec = baseDecorator(decoratorFun, kwsyntax=True)  # type: ignore[reportCallIssue]

    def _decoratorForSlotInner(fun=None, *args, **kwargs):
        if fun is None:  # maybe this is a factory decorator
            return _decoratorForSlotInner

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


def _extractLoggerInner(decoratedFun) -> logging.Logger | None:
    if mod := sys.modules.get(decoratedFun.__module__, None):
        return getattr(mod, 'logger', None)
    return None


def _extractLogger(decObj):
    def _extractLoggerFunOrArg(decoratedFun=None, logger=None):
        nonlocal decObj

        match decoratedFun, logger:
            case None, None:  # called with no args
                return _extractLoggerFunOrArg

            case None, logging.Logger():
                return partial(_extractLoggerFunOrArg, logger=logger)

            case None, _:
                msg = f"Unknown logger parameter type {type(logger)}"
                raise TypeError(msg)

            case decoratedFun, _ if not callable(decoratedFun):
                msg = f"decoratedFun must be a function, got {decoratedFun}"
                raise TypeError(msg)

            case decoratedFun, logging.Logger():
                return decObj(decoratedFun, logger)

            case decoratedFun, None:
                if (logger := _extractLoggerInner(decoratedFun)) is None:
                    # we use default logger defined in a decorator
                    return decObj(decoratedFun)
                return decObj(decoratedFun, logger)

            case _:
                msg = "Unknown logger parameters"
                raise TypeError(msg)

    return _extractLoggerFunOrArg


@_extractLogger
@decoratorForSlot
def exceptionDecFactory(
    fun, logger=_moduleLogger, level=logging.ERROR, *args, **kwargs
):
    try:
        return fun(*args, **kwargs)
    except Exception:
        logger.log(level, "Unknown exception", exc_info=True)
        raise


@_extractLogger
@decoratorForSlot
def entryExitDecFactory(fun, logger=_moduleLogger, *args, **kwargs):
    logger.debug(f"Before: {fun.__name__}")
    result = fun(*args, **kwargs)
    logger.debug(f"After: {fun.__name__}")
    return result


@_extractLogger
@decoratorForSlot
def timeDecFactory(fun, logger=_moduleLogger, *args, **kwargs):
    start = time.time()
    try:
        return fun(*args, **kwargs)
    finally:
        logger.debug(f"{fun.__name__}, execute time:{time.time() - start :.4f}s")


@decoratorForSlot
def cursorDecFactory(fun, cursor=Qt.WaitCursor, *args, **kwargs):
    QApplication.setOverrideCursor(cursor)
    try:
        return fun(*args, **kwargs)
    finally:
        QApplication.restoreOverrideCursor()


@decoratorForSlot
def singleCallDecFactory(
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
