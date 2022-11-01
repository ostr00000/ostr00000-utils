import collections
from datetime import datetime
from typing import TypeVar, Callable, Protocol, cast

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
def _changeStatusDec(fun, msg='', failureMsg='', returnValue=True,
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


Fun_t = TypeVar('Fun_t', bound=Callable)


class StatusDec_t(Protocol):
    def __call__(self, *, msg: str = '', failureMsg: str = '', returnValue: bool = True) \
            -> Callable[[Fun_t], Fun_t]: ...


changeStatusDec = cast(StatusDec_t, _changeStatusDec)
