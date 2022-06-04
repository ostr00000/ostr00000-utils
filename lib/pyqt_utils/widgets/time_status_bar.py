import collections
from datetime import datetime

from PyQt5.QtWidgets import QStatusBar
from decorator import decorator


class TimeStatusBar(QStatusBar):
    HISTORY_SIZE = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = collections.deque(maxlen=self.HISTORY_SIZE)

    def showMessage(self, message: str, timeout: int = 0):
        msg = f'{datetime.now().strftime("%H:%M:%S.%f")[:-4]} :  {message}'
        self._history.append(msg)
        self.setToolTip('\n'.join(self._history))
        return super().showMessage(msg, timeout)


@decorator
def changeStatusDec(fun, msg: str = '', failureMsg='', returnValue=1,
                    *args, **kwargs):
    """
    None -> (skip decorator)
    False -> failureMsg
    _ -> msg
    """
    val = fun(*args, **kwargs)
    if val is False:
        msg = failureMsg
    elif val is None:
        return val

    self = args[0]
    try:
        statusBar = self.statusBar()
    except AttributeError:
        statusBar = self.parent().statusBar()

    statusBar.showMessage(msg)
    if returnValue:
        return val
