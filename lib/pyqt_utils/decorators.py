from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from decorator import decorator


@decorator
def cursorDec(fun, cursor=Qt.WaitCursor, *args, **kwargs):
    QApplication.setOverrideCursor(cursor)
    try:
        return fun(*args, **kwargs)
    finally:
        QApplication.restoreOverrideCursor()
