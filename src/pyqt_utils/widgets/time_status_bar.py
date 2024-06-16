import collections
from datetime import UTC, datetime

from PyQt5.QtWidgets import QStatusBar


class TimeStatusBar(QStatusBar):
    HISTORY_SIZE = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self._history = collections.deque(maxlen=self.HISTORY_SIZE)

    def showMessage(self, message: str, timeout: int = 0):
        d = datetime.now(UTC).astimezone()
        msg = f'{d.strftime("%H:%M:%S.%f")[:-4]} :  {message}'
        self._history.append(msg)
        self.setToolTip('\n'.join(self._history))
        return super().showMessage(msg, timeout)
