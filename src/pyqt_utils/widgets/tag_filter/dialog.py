from __future__ import annotations

import copy
import logging
from typing import TYPE_CHECKING

from PyQt5.QtCore import QItemSelectionModel, QModelIndex, QStringListModel, Qt
from PyQt5.QtTest import QAbstractItemModelTester
from PyQt5.QtWidgets import QCompleter, QDialog, QListWidget

from pyqt_utils.qobjects.substring_validator import SubstringValidator
from pyqt_utils.ui.tag_dialog_ui import Ui_TagDialog
from pyqt_utils.widgets.base_ui_widget import BaseUiWidget
from pyqt_utils.widgets.tag_filter.model import TagFilterModel
from pyqt_utils.widgets.tag_filter.nodes import (
    TagFilterAndNode,
    TagFilterOrNode,
    TagFilterSequenceNode,
)

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logging.getLogger(__name__)


class TagFilterDialog(Ui_TagDialog, QDialog, BaseUiWidget):
    _activeListWidget: None | QListWidget
    _possibleValues: list[str]

    def __post_init__(
        self,
        *args,
        existingNode: TagFilterOrNode | None = None,
        possibleValues: Iterable[str] = (),
        **kwargs,
    ):
        super().__post_init__(*args, **kwargs)
        self.setPossibleValues(possibleValues)

        self._tagModel = TagFilterModel(existingNode)
        self._tagModel.rowsInserted.connect(self.onIncludeRowsInserted)
        self._tagModel.rowsMoved.connect(self.onIncludeRowsMoved)
        self._tagModel.dataChanged.connect(self.onIncludeRowsMoved)
        self._testModel = QAbstractItemModelTester(
            self._tagModel, QAbstractItemModelTester.FailureReportingMode.Warning, self
        )
        self.expressionTree.setModel(self._tagModel)
        self.expressionTree.expandAll()
        self.expressionTree.setAcceptDrops(True)

        self.includeButton.clicked.connect(self.onIncludeClicked)
        self.removeButton.clicked.connect(self.onRemoveClicked)
        self.orButton.clicked.connect(self.onOrClicked)
        self.andButton.clicked.connect(self.onAndClicked)
        self.negateButton.clicked.connect(self.onNegateClicked)

        self.searchLineEdit.setCompleter(QCompleter(self._possibleValues, self))
        self.searchLineEdit.setValidator(SubstringValidator(self._possibleValues, self))
        self.searchLineEdit.textChanged.connect(self.onSearchLineTextChanged)

        self._tagModel.failureCause.connect(self.statusBar.showMessage)

    def setPossibleValues(self, values: Iterable[str]):
        self._possibleValues = sorted(set(values))
        self.possibleTagsWidget.clear()
        self.possibleTagsWidget.addItems(self._possibleValues)

        if comp := self.searchLineEdit.completer():
            if isinstance(model := comp.model(), QStringListModel):
                model.setStringList(values)
            else:
                logger.warning("Unsupported completion model")

        if isinstance(validator := self.searchLineEdit.validator(), SubstringValidator):
            validator.setPossibleValues(self._possibleValues)

    def onIncludeRowsInserted(self, parent: QModelIndex, first: int, last: int):
        self._expandView(parent, first, last)

    def onIncludeRowsMoved(
        self,
        _parent: QModelIndex,
        start: int,
        end: int,
        destination: QModelIndex,
        row: int,
    ):
        self._expandView(destination, row, end - start)

    def _expandView(self, parent: QModelIndex, first: int, last: int):
        for row in range(first, last + 1):
            self.expressionTree.expandRecursively(self._tagModel.index(row, 0, parent))

    def onIncludeClicked(self):
        if indexes := self.possibleTagsWidget.selectedIndexes():
            includeItem = self.expressionTree.currentIndex()
            for i in indexes:
                self._tagModel.addSimple(i.data(), includeItem)

    def onRemoveClicked(self):
        if indexes := self.expressionTree.selectedIndexes():
            self._tagModel.removeIndexes(indexes)
            self._refreshAfterAction(self._tagModel.topLevelIndex)

    def _refreshAfterAction(self, currentModel: QModelIndex):
        sm = self.expressionTree.selectionModel()
        sm.select(currentModel, QItemSelectionModel.ClearAndSelect)
        sm.setCurrentIndex(currentModel, QItemSelectionModel.SelectCurrent)

    def onOrClicked(self):
        self._addRule(TagFilterOrNode)

    def onAndClicked(self):
        self._addRule(TagFilterAndNode)

    def _addRule(self, nodeType: type[TagFilterSequenceNode]):
        indexes = self.expressionTree.selectedIndexes()
        if mergedIndex := self._tagModel.mergeTags(nodeType, indexes):
            self._refreshAfterAction(mergedIndex)

    def onNegateClicked(self):
        indexes = self.expressionTree.selectedIndexes()
        if len(indexes) == 1:
            self._tagModel.negate(indexes[0])

    def onSearchLineTextChanged(self, newText: str):
        if founded := self.possibleTagsWidget.findItems(newText, Qt.MatchFixedString):
            f = founded[0]  # all items should be unique
            self.possibleTagsWidget.setCurrentItem(f)

    def getValue(self):
        return copy.deepcopy(self._tagModel.topNode)
