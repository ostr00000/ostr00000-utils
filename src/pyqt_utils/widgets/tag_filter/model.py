import copy
import logging
import pickle
from collections.abc import Iterable

from PyQt5.QtCore import QAbstractItemModel, QMimeData, QModelIndex, Qt, pyqtSignal
from PyQt5.QtGui import QStandardItemModel

from pyqt_utils.widgets.tag_filter.nodes import (
    TagFilterExcludeNode,
    TagFilterNode,
    TagFilterOrNode,
    TagFilterSequenceNode,
)

logger = logging.getLogger(__name__)
NodePath_T = tuple[int, ...]
NodePaths_T = list[NodePath_T]


class TagFilterModel(QAbstractItemModel):
    failureCause = pyqtSignal(str)

    @classmethod
    def _checkType[T](cls, var, expectedType: type[T] = TagFilterNode) -> T:
        if not isinstance(var, expectedType):
            msg = f"Expected {expectedType}, got {type(var)}"
            raise TypeError(msg)
        return var

    @classmethod
    def _getFromInternalPointer[T](
        cls, index: QModelIndex, expectedType: type[T] = TagFilterNode
    ) -> T:
        return cls._checkType(index.internalPointer(), expectedType)

    def __init__(self, topNode: TagFilterOrNode | None = None):
        super().__init__()
        if topNode is None:
            self.topNode = TagFilterOrNode()
        else:
            self.topNode = copy.deepcopy(topNode)

        self._checkType(self.topNode)
        self.topLevelIndex = self.createIndex(0, 0, self.topNode)
        self.failureCause.connect(logger.debug)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return [self.tr("Tag")][section]
        return None

    def rowCount(self, curIndex: QModelIndex = QModelIndex()) -> int:
        if not curIndex.isValid():
            return 1

        node = self._getFromInternalPointer(curIndex)
        return len(node)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parentNode = self._getFromInternalPointer(parent, TagFilterSequenceNode)
            curNode = parentNode.tagList[row]
        else:
            curNode = self.topNode

        self._checkType(curNode)
        return self.createIndex(row, column, curNode)

    def parent(self, child: QModelIndex) -> QModelIndex:
        if not child.isValid():
            return QModelIndex()

        curNode: TagFilterNode = child.internalPointer()
        if (parentNode := curNode.parent) is None:
            return QModelIndex()

        return self._getIndexFromNode(parentNode)

    def _getIndexFromNode(self, curNode: TagFilterNode):
        if (parentNode := curNode.parent) is None:
            parentRow = 0
        else:
            parentNode = self._checkType(parentNode, TagFilterSequenceNode)
            parentRow = next(
                i for i, n in enumerate(parentNode.tagList) if n == curNode
            )

        self._checkType(curNode)
        return self.createIndex(parentRow, 0, curNode)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None

        match role:
            case Qt.DisplayRole | Qt.ToolTipRole:
                data: TagFilterNode = index.internalPointer()
                return str(data)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        if not index.isValid():  # root index / dropping on viewport
            return flags | Qt.ItemIsDropEnabled

        match index.internalPointer():
            case self.topNode:
                return flags | Qt.ItemIsDropEnabled
            case TagFilterSequenceNode():
                return flags | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled
            case _:
                return flags | Qt.ItemIsDragEnabled

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction | Qt.CopyAction

    TAG_FILTER_MIME = 'application/tag_filter_indexes'
    QT_MIME = 'application/x-qabstractitemmodeldatalist'

    def mimeTypes(self) -> list[str]:
        return [self.TAG_FILTER_MIME, self.QT_MIME]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        md = QMimeData()
        nodePaths = self._filterRepeatedParentNodes(indexes)
        md.setData(self.TAG_FILTER_MIME, pickle.dumps(nodePaths))
        return md

    def _filterRepeatedParentNodes(self, indexes: Iterable[QModelIndex]) -> NodePaths_T:
        nodePathToIndex: dict[NodePath_T, QModelIndex] = {}
        allNodes: dict[TagFilterNode, QModelIndex] = {
            ind.internalPointer(): ind for ind in indexes
        }
        for node, ind in allNodes.items():
            nodePath = []
            prevNode = node
            nodeParent = node
            while nodeParent := nodeParent.parent:
                if nodeParent in allNodes:
                    break

                nodeParent = self._checkType(nodeParent, TagFilterSequenceNode)
                nodePath.append(nodeParent.tagList.index(prevNode))
                prevNode = nodeParent

            else:
                nodePathToIndex[tuple(reversed(nodePath))] = ind

        return sorted(nodePathToIndex)

    def dropMimeData(
        self,
        mimeData: QMimeData,
        action: Qt.DropAction,
        row: int,
        column: int,
        parentIndex: QModelIndex,
    ) -> bool:
        if action == Qt.CopyAction and mimeData.hasFormat(self.QT_MIME):
            return self._dropSimpleData(parentIndex, mimeData, row)

        if action == Qt.MoveAction and mimeData.hasFormat(self.TAG_FILTER_MIME):
            byteObj = mimeData.data(self.TAG_FILTER_MIME).data()
            # SKIP: TODO [P2]: temporary ignored, maybe this could be a json?
            nodePaths: NodePaths_T = pickle.loads(byteObj)  # noqa: S301
            return self._dropNodePath(parentIndex, nodePaths, row)

        return False

    def _dropSimpleData(
        self, parentIndex: QModelIndex, mimeData: QMimeData, row: int
    ) -> bool:
        model = QStandardItemModel()
        model.dropMimeData(mimeData, Qt.CopyAction, 0, 0, QModelIndex())
        if model.columnCount() != 1:
            msg = self.tr("Unsupported column size: {}, expected 1")
            self.failureCause.emit(msg.format(model.columnCount()))
            return False

        values = [model.item(rowNum, 0).text() for rowNum in range(model.rowCount())]
        if row == -1:
            for val in values:
                self.addSimple(val, parentIndex)
        else:
            for i, val in enumerate(values, row):
                self.addSimple(val, parentIndex, i)

        return True

    def _dropNodePath(
        self, parentIndex: QModelIndex, nodePaths: NodePaths_T, first: int = -1
    ) -> bool:
        if parentIndex.isValid():
            nodeParent = parentIndex.internalPointer()
        else:
            nodeParent = self.topNode
            parentIndex = self.topLevelIndex
        nodeParent = self._checkType(nodeParent, TagFilterSequenceNode)

        if nodeParent == self.topNode and first == 1:
            # special case when we place an item at the top level
            first = -1

        nodes = [self._getNodeFromNodePath(np) for np in nodePaths]
        indexes = [self._getIndexFromNode(node) for node in nodes]

        if first > 0:
            # find first position after indexes removal
            for ind in sorted(indexes, key=lambda i: -i.row()):
                if ind.parent() == parentIndex and ind.row() < first:
                    first -= 1

        self.removeIndexes(indexes)

        if first == -1:  # we append at the end
            first = len(nodeParent.tagList)

        self.beginInsertRows(parentIndex, first, first + len(nodePaths) - 1)
        for pos, node in enumerate(nodes, first):
            nodeParent.insert(pos, node)
        self.endInsertRows()
        return True

    def _getNodeFromNodePath(self, nodePath: NodePath_T):
        node = self.topNode
        for p in nodePath:
            node = self._checkType(node, TagFilterSequenceNode)
            node = node.tagList[p]
        return node

    def addSimple(self, text: str, parent: QModelIndex, row: int | None = None) -> bool:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self.topNode
            parent = self.topLevelIndex

        if not isinstance(node, TagFilterSequenceNode):
            self.failureCause.emit(self.tr("Index is not of sequence type"))
            return False

        for t in node.tagList:
            if t.tagName == text:
                msg = self.tr("Tag with name: {} already exist")
                self.failureCause.emit(msg.format(text))
                return False

        if row is None:
            row = len(node.tagList)
        self.beginInsertRows(parent, row, row)
        tn = TagFilterNode(tagName=text, parent=node)
        node.insert(row, tn)
        self.endInsertRows()
        return True

    def mergeTags(
        self, nodeType: type[TagFilterSequenceNode], indexes: list[QModelIndex]
    ) -> QModelIndex | None:
        if self._isIndexInvalid(*indexes):
            return None

        indexParent = indexes[0].parent()
        nodeParent: TagFilterSequenceNode = indexParent.internalPointer()
        firstNodeIndex = len(nodeParent)
        for ind in indexes:
            if ind.parent() != indexParent:
                self.failureCause.emit(self.tr("Indexes have different parents"))
                return None

            index = nodeParent.tagList.index(ind.internalPointer())
            firstNodeIndex = min(firstNodeIndex, index)

        nodes = self.removeIndexes(indexes)
        if not nodes:
            msg = "Cannot remove indexes - returned empty list"
            raise ValueError(msg)

        self.beginInsertRows(indexParent, firstNodeIndex, firstNodeIndex)
        mergedNode = nodeType(tagList=nodes, parent=nodeParent)
        nodeParent.insert(firstNodeIndex, mergedNode)
        self.endInsertRows()

        return self.index(firstNodeIndex, 0, indexParent)

    def removeIndexes(self, indexes: list[QModelIndex]) -> list[TagFilterNode]:
        if self._isIndexInvalid(*indexes):
            return []

        sortedIndexes = sorted(indexes, key=lambda i: -i.row())
        return [self._remove(ind) for ind in sortedIndexes]

    def _remove(self, curIndex: QModelIndex):
        node = self._getFromInternalPointer(curIndex)
        parentNode = self._checkType(node.parent, TagFilterSequenceNode)

        self.beginRemoveRows(curIndex.parent(), curIndex.row(), curIndex.row())
        parentNode.remove(node)
        self.endRemoveRows()
        return node

    def _isIndexInvalid(self, *indexes: QModelIndex) -> bool:
        if not indexes:
            self.failureCause.emit(self.tr("There is no index"))
            return True
        for index in indexes:
            if not index.isValid():
                self.failureCause.emit(self.tr("The index is invalid"))
                return True
            if index == self.topLevelIndex:
                self.failureCause.emit(self.tr("Cannot use top level index"))
                return True
        return False

    def negate(self, index: QModelIndex):
        if self._isIndexInvalid(index):
            return None

        node = self._getFromInternalPointer(index)
        parentNode = self._checkType(node.parent, TagFilterSequenceNode)

        row = index.row()
        indexParent = index.parent()
        self.removeIndexes([index])

        self.beginInsertRows(indexParent, row, row)
        if isinstance(node, TagFilterExcludeNode):
            nodeContent = node.content
        else:
            nodeContent = TagFilterExcludeNode(node)
        parentNode.insert(row, nodeContent)
        self.endInsertRows()
        return True
