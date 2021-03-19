import inspect
import logging
import sys
import time
import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from decorator import decorator

from pyqt_utils.python.logger_skip_frame import SkipFrameInModule

SkipFrameInModule(__file__)
_moduleLogger = logging.getLogger(__name__)


def _extractLogger(decObj):
    def _extractLoggerFunOrArg(decoratedFun=None, logger=None):
        nonlocal decObj
        if decoratedFun is None:
            assert logger is not None
            return decObj(logger=logger)

        assert inspect.isfunction(decoratedFun)
        if logger is None:
            if mod := sys.modules.get(decoratedFun.__module__, None):
                logger = getattr(mod, 'logger', None)

        if logger:
            return decObj(decoratedFun, logger)
        return decObj(decoratedFun)

    return _extractLoggerFunOrArg


@_extractLogger
@decorator
def exceptionDec(fun, logger=_moduleLogger, *args, **kwargs):
    try:
        return fun(*args, **kwargs)
    except Exception:
        logger.debug(str(traceback.format_exc()))
        raise


@_extractLogger
@decorator
def actionDec(fun, logger=_moduleLogger, *args, **kwargs):
    logger.debug(f"Before: {fun.__name__}")
    result = fun(*args, **kwargs)
    logger.debug(f"After: {fun.__name__}")
    return result


@_extractLogger
@decorator
def timeDec(fun, logger=_moduleLogger, *args, **kwargs):
    start = time.time()
    try:
        return fun(*args, **kwargs)
    finally:
        logger.debug(f"{fun.__name__}, execute time:{time.time() - start :.4f}s")


@_extractLogger
@decorator
def safeRun(fun, logger=_moduleLogger, *args, **kwargs):
    try:
        return fun(*args, **kwargs)
    except Exception as exc:
        logger.error(f'{exc}\n{traceback.format_exc()}')


@decorator
def cursorDec(fun, cursor=Qt.WaitCursor, *args, **kwargs):
    QApplication.setOverrideCursor(cursor)
    try:
        return fun(*args, **kwargs)
    finally:
        QApplication.restoreOverrideCursor()
