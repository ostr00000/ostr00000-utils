from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QScrollArea, QVBoxLayout

from pyqt_utils.widgets.space_line_edit import SpaceLineEdit


class MultiLevelSpaceLineEdit(SpaceLineEdit):
    WIDGET_IN_ROW = 9

    def _initStartWidget(self):
        self._mainLayout = QVBoxLayout(self)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        self._hLayouts = [self._createLayout()]
        self._mainLayout.addStretch()

    def _createLayout(self):
        layout = super()._createLayout()
        self._mainLayout.insertLayout(self._mainLayout.count() - 1, layout)
        return layout

    def _refreshLayout(self):
        widgetToLayout: dict[QLineEdit, QHBoxLayout] = {
            lay.itemAt(i).widget(): lay
            for lay in self._hLayouts
            for i in range(lay.count())
        }

        for w, lay in widgetToLayout.items():
            if w and w not in self._lineEdits:
                lay.removeWidget(w)
                w.deleteLater()

        layoutCount = -1
        currentLayout = self._hLayouts[0]
        for i, le in enumerate(self._lineEdits):
            if i % self.WIDGET_IN_ROW == 0:
                layoutCount += 1
                if layoutCount >= len(self._hLayouts):
                    self._hLayouts.append(self._createLayout())
                currentLayout = self._hLayouts[layoutCount]

            if le not in widgetToLayout:
                currentLayout.insertWidget(i % self.WIDGET_IN_ROW, le)
            else:
                oldLayout = widgetToLayout[le]
                if oldLayout != currentLayout:
                    oldLayout.removeWidget(le)
                    currentLayout.addWidget(le)
                item = currentLayout.itemAt(i % self.WIDGET_IN_ROW)
                if item and item.widget() != le:
                    oldItem = currentLayout.replaceWidget(item.widget(), le)
                    currentLayout.addItem(oldItem)

        for oldLayout in self._hLayouts[layoutCount + 1 :]:
            oldLayout.deleteLater()
        del self._hLayouts[layoutCount + 1 :]


class ScrollSpaceLineEdit(QScrollArea):
    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)
        self.sle = MultiLevelSpaceLineEdit(parent=self, **kwargs)
        self.setWidget(self.sle)
        self.setWidgetResizable(True)

    def getValues(self):
        return self.sle.getValues()

    def setValues(self, values: list[str]):
        return self.sle.setValues(values)
