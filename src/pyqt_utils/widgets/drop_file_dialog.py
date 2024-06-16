import logging
import typing

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QFileDialog, QWidget

logger = logging.getLogger(__name__)


class DropFileDialog(QFileDialog):
    @typing.overload
    def __init__(
        self,
        parent: QWidget,
        f: Qt.WindowFlags | Qt.WindowType,
    ) -> None: ...

    # noinspection PyShadowingBuiltins
    @typing.overload
    def __init__(
        self,
        parent: QWidget | None = ...,
        caption: str = ...,  # noqa: F841 # SKIP: false positive in vulture
        directory: str = ...,  # noqa: F841 # SKIP: false positive in vulture
        # SKIP: shadows builtin, but this defined in Qt API
        filter: str = ...,  # noqa: A002
    ) -> None: ...

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
            if len(formattedUrls) > 1:
                self.selectFile(''.join(formattedUrls))
        else:
            super().dropEvent(dropEvent)

    def dragEnterEvent(self, dragEnterEvent: QDragEnterEvent) -> None:
        if dragEnterEvent.mimeData().hasUrls():
            dragEnterEvent.acceptProposedAction()
        else:
            super().dragEnterEvent(dragEnterEvent)
