import logging

from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)


class DropFileDialog(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)

    def dropEvent(self, dropEvent: QDropEvent) -> None:
        if dropEvent.mimeData().hasUrls():
            formattedUrls = []
            for url in dropEvent.mimeData().urls():
                if not url.isLocalFile():
                    continue

                self.selectUrl(url)
                formattedUrls.append(f'"{url.toLocalFile()}"')
            logger.debug(f"Selected files: {formattedUrls}")
            self.selectFile(''.join(formattedUrls))
        else:
            super().dropEvent(dropEvent)

    def dragEnterEvent(self, dragEnterEvent: QDragEnterEvent) -> None:
        if dragEnterEvent.mimeData().hasUrls():
            dragEnterEvent.acceptProposedAction()
        else:
            super().dragEnterEvent(dragEnterEvent)
