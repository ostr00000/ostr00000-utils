from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QWidget


class WindowModifiedPropagator(QWidget):
    def event(self, event: QEvent):
        if event.type() == QEvent.ModifiedChange:
            p = self.parent()
            if isinstance(p, QWidget):
                p.setWindowModified(self.isWindowModified())

        return super().event(event)
