import logging
from functools import wraps

from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog

logger = logging.getLogger(__name__)


class DropFileDialog(QFileDialog):

    @wraps(QFileDialog.__init__, ('__annotations__',))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setMinimumHeight(600)
        self.setMinimumWidth(800)

    def dropEvent(self, dropEvent: QDropEvent) -> None:
        if not dropEvent.mimeData().hasUrls():
            return super().dropEvent(dropEvent)

        formattedUrls = []
        for url in dropEvent.mimeData().urls():
            if not url.isLocalFile():
                continue

            self.selectUrl(url)
            formattedUrls.append(f'"{url.toLocalFile()}"')

        logger.debug(f"Selected files: {formattedUrls}")
        if len(formattedUrls) > 1:
            self.selectFile(''.join(formattedUrls))
            return None
        return None

    def dragEnterEvent(self, dragEnterEvent: QDragEnterEvent) -> None:
        if dragEnterEvent.mimeData().hasUrls():
            dragEnterEvent.acceptProposedAction()
        else:
            super().dragEnterEvent(dragEnterEvent)
