from __future__ import annotations

import logging

from PyQt5.QtCore import QModelIndex, Qt, QItemSelectionModel
from PyQt5.QtWidgets import QDialog, QListWidget, QTreeView, QCompleter

from pyqt_utils.qobjects.substring_validator import SubstringValidator
from pyqt_utils.ui.include_exclude_dialog_ui import Ui_IncludeExcludeDialog
from pyqt_utils.widgets.base_widget import BaseWidget
from pyqt_utils.widgets.include_exclude.model import IncludeExcludeModel
from pyqt_utils.widgets.include_exclude.nodes import TagFilterOrNode, TagFilterAndNode, \
    TagFilterSequenceNode

logger = logging.getLogger(__name__)


class IncludeExcludeFilterDialog(Ui_IncludeExcludeDialog, BaseWidget, QDialog):
    _activeListWidget: None | QListWidget

    def __post_init__(self, *args,
                      includeValues: TagFilterOrNode = None,
                      excludeValues: TagFilterOrNode = None,
                      possibleValues: list[str],
                      **kwargs):
        super().__post_init__(*args, **kwargs)
        self._possibleValues = sorted(possibleValues)

        self._includeModel = IncludeExcludeModel(includeValues)
        self._includeModel.rowsInserted.connect(self.onIncludeRowsInserted)
        self._includeModel.rowsMoved.connect(self.onIncludeRowsMoved)
        self.includeView.setModel(self._includeModel)
        self.includeView.expandAll()

        self._excludeModel = IncludeExcludeModel(excludeValues)
        self._excludeModel.rowsInserted.connect(self.onExcludeRowsInserted)
        self._excludeModel.rowsMoved.connect(self.onExcludeRowsMoved)
        self.excludeView.setModel(self._excludeModel)
        self.excludeView.expandAll()
        self.possibleTagsWidget.addItems(self._possibleValues)

        self.includeButton.clicked.connect(self.onInclude)
        self.excludeButton.clicked.connect(self.onExclude)
        self.removeIncludeButton.clicked.connect(self.onRemoveInclude)
        self.removeExcludeButton.clicked.connect(self.onRemoveExclude)
        self.orIncludeButton.clicked.connect(self.onOrInclude)
        self.orExcludeButton.clicked.connect(self.onOrExclude)
        self.andIncludeButton.clicked.connect(self.onAndInclude)
        self.andExcludeButton.clicked.connect(self.onAndExclude)

        self.searchLineEdit.setCompleter(QCompleter(self._possibleValues, self))
        self.searchLineEdit.setValidator(SubstringValidator(self._possibleValues, self))
        self.searchLineEdit.textChanged.connect(self.onSearchLineTextChanged)

    def onIncludeRowsInserted(self, parent: QModelIndex, first: int, last: int):
        self._expandView(self.includeView, parent, first, last)

    def onExcludeRowsInserted(self, parent: QModelIndex, first: int, last: int):
        self._expandView(self.excludeView, parent, first, last)

    def onIncludeRowsMoved(self, _parent: QModelIndex, start: int, end: int,
                           destination: QModelIndex, row: int):
        self._expandView(self.includeView, destination, row, end - start)

    def onExcludeRowsMoved(self, _parent: QModelIndex, start: int, end: int,
                           destination: QModelIndex, row: int):
        self._expandView(self.excludeView, destination, row, end - start)

    def _expandView(self, view: QTreeView, parent: QModelIndex, first: int, last: int):
        model = parent.model()
        for row in range(first, last + 1):
            view.expand(model.index(row, 0, parent))

    def onInclude(self):
        self._addToModel(self.includeView, self._includeModel)

    def onExclude(self):
        self._addToModel(self.excludeView, self._excludeModel)

    def _addToModel(self, view: QTreeView, model: IncludeExcludeModel):
        if indexes := self.possibleTagsWidget.selectedIndexes():
            includeItem = view.currentIndex()
            for i in indexes:
                model.addSimple(i.data(), includeItem)

    def onRemoveInclude(self):
        self._removeFromModel(self.includeView, self._includeModel)

    def onRemoveExclude(self):
        self._removeFromModel(self.excludeView, self._excludeModel)

    def _removeFromModel(self, view: QTreeView, model: IncludeExcludeModel):
        if indexes := view.selectedIndexes():
            for i in indexes:
                model.remove(i)
            self._refreshAfterAction(view, model.topLevelModel)

    def _refreshAfterAction(self, view: QTreeView, currentModel: QModelIndex):
        view.selectionModel().select(currentModel, QItemSelectionModel.ClearAndSelect)
        view.selectionModel().setCurrentIndex(currentModel, QItemSelectionModel.SelectCurrent)
        view.expandAll()

    def onOrInclude(self):
        self._addRule(self.includeView, self._includeModel, TagFilterOrNode)

    def onOrExclude(self):
        self._addRule(self.excludeView, self._excludeModel, TagFilterOrNode)

    def onAndInclude(self):
        self._addRule(self.includeView, self._includeModel, TagFilterAndNode)

    def onAndExclude(self):
        self._addRule(self.excludeView, self._excludeModel, TagFilterAndNode)

    def _addRule(self, view: QTreeView, model: IncludeExcludeModel,
                 nodeType: type[TagFilterSequenceNode]):
        if mergedIndex := model.mergeTags(nodeType, view.selectedIndexes()):
            self._refreshAfterAction(view, mergedIndex)

    def onSearchLineTextChanged(self, newText: str):
        if newText not in self._possibleValues:
            return

        if founded := self.possibleTagsWidget.findItems(newText, Qt.MatchFixedString):
            f = founded[0]  # all items should be unique
            self.possibleTagsWidget.setCurrentItem(f)

    def getValues(self):
        return self._includeModel.topNode, self._excludeModel.topNode
