import copy
import logging
import pickle
from collections.abc import Iterable

from PyQt5.QtCore import QModelIndex, QAbstractItemModel, Qt, QMimeData
from PyQt5.QtGui import QStandardItemModel

from pyqt_utils.widgets.include_exclude.nodes import TagFilterNode, TagFilterSequenceNode, \
    TagFilterOrNode

logger = logging.getLogger(__name__)
NodePath_T = tuple[int, ...]
NodePaths_T = list[NodePath_T]


class IncludeExcludeModel(QAbstractItemModel):
    def __init__(self, topNode: TagFilterOrNode = None):
        super().__init__()
        if topNode is None:
            self.topNode = TagFilterOrNode()
        else:
            self.topNode = copy.deepcopy(topNode)
        self.topLevelModel = self.createIndex(0, 0, self.topNode)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return [self.tr("Tag")][section]

    def rowCount(self, curIndex: QModelIndex = QModelIndex()) -> int:
        if not curIndex.isValid():
            return 1

        node: TagFilterNode = curIndex.internalPointer()
        return len(node)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 1

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parentNode: TagFilterNode = parent.internalPointer()
            assert isinstance(parentNode, TagFilterSequenceNode)
            curNode = parentNode.tagList[row]
        else:
            curNode = self.topNode

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
            assert isinstance(parentNode, TagFilterSequenceNode)
            parentRow = next(i for i, n in enumerate(parentNode.tagList)
                             if n == curNode)

        return self.createIndex(parentRow, 0, curNode)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return

        match role:
            case Qt.DisplayRole | Qt.ToolTipRole:
                data: TagFilterNode = index.internalPointer()
                return str(data)

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        flags = super().flags(index)
        match index.internalPointer():
            case self.topNode:
                return flags | Qt.ItemIsDropEnabled
            case TagFilterSequenceNode():
                return flags | Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled
            case _:
                return flags | Qt.ItemIsDragEnabled

    def supportedDropActions(self) -> Qt.DropActions:
        return Qt.MoveAction | Qt.CopyAction

    INC_EXC_MIME = 'application/include_exclude_indexes'
    QT_MIME = 'application/x-qabstractitemmodeldatalist'

    def mimeTypes(self) -> list[str]:
        return [self.INC_EXC_MIME, self.QT_MIME]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        md = QMimeData()
        nodePaths = self._filterRepeatedParentNodes(indexes)
        md.setData(self.INC_EXC_MIME, pickle.dumps(nodePaths))
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

                assert isinstance(nodeParent, TagFilterSequenceNode)
                nodePath.append(nodeParent.tagList.index(prevNode))
                prevNode = nodeParent

            else:
                nodePathToIndex[tuple(reversed(nodePath))] = ind

        return sorted(nodePathToIndex)

    def dropMimeData(self, mimeData: QMimeData, action: Qt.DropAction,
                     row: int, column: int, parentIndex: QModelIndex) -> bool:
        if action == Qt.CopyAction and mimeData.hasFormat(self.QT_MIME):
            return self._dropSimpleData(parentIndex, mimeData, row)

        if action == Qt.MoveAction and mimeData.hasFormat(self.INC_EXC_MIME):
            nodePaths: NodePaths_T = pickle.loads(mimeData.data(self.INC_EXC_MIME))
            return self._dropNodePath(parentIndex, nodePaths, row)

    def _dropSimpleData(self, parentIndex: QModelIndex, mimeData: QMimeData, row: int):
        model = QStandardItemModel()
        model.dropMimeData(mimeData, Qt.CopyAction, 0, 0, QModelIndex())
        if model.columnCount() != 1:
            return False

        counter = 0
        for rowNum in range(model.rowCount()):
            text = model.item(rowNum, 0).text()
            if self.addSimple(text, parentIndex, row + counter):
                counter += 1

        return True

    def _dropNodePath(self, parentIndex: QModelIndex,
                      nodePaths: NodePaths_T, first: int = -1) -> bool:
        nodeParent = parentIndex.internalPointer()
        assert isinstance(nodeParent, TagFilterSequenceNode)

        nodes = [self._getNodeFromNodePath(np) for np in nodePaths]
        indexes = [self._getIndexFromNode(node) for node in nodes]
        indexesSorted = sorted(indexes, key=lambda i: -i.row())
        for ind in indexesSorted:
            if ind.parent() == parentIndex and ind.row() < first:
                first -= 1
            self.remove(ind)

        if first == -1:
            first = len(nodeParent.tagList)
        self.beginInsertRows(parentIndex, first, first + len(nodePaths) - 1)
        for pos, node in enumerate(nodes, first):
            nodeParent.tagList.insert(pos, node)
            node.parent = nodeParent
        self.endInsertRows()
        return True

    def _getNodeFromNodePath(self, nodePath: NodePath_T):
        node = self.topNode
        for p in nodePath:
            assert isinstance(node, TagFilterSequenceNode)
            node = node.tagList[p]
        return node

    def addSimple(self, text: str, parent: QModelIndex, row: int = None) -> bool:
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self.topNode
            parent = self.topLevelModel

        if not isinstance(node, TagFilterSequenceNode):
            return False

        for t in node.tagList:
            if t.tagName == text:
                return False

        if row is None:
            row = len(node.tagList)
        self.beginInsertRows(parent, row, row)
        tn = TagFilterNode(tagName=text, parent=node)
        node.tagList.insert(row, tn)
        self.endInsertRows()
        return True

    def mergeTags(self, nodeType: type[TagFilterSequenceNode], indexes: list[QModelIndex]
                  ) -> QModelIndex | None:
        if not indexes:
            logger.debug("No index to merge")
            return

        indexParent = indexes[0].parent()
        nodeParent: TagFilterSequenceNode = indexParent.internalPointer()
        firstNodeIndex = len(nodeParent)
        for ind in indexes:
            if not ind.isValid():
                return
            if ind == self.topLevelModel:
                return
            if ind.parent() != indexParent:
                logger.debug("Indexes have different parents")
                return

            firstNodeIndex = min(firstNodeIndex, nodeParent.tagList.index(ind.internalPointer()))

        indexesSorted = sorted(indexes, key=lambda i: -i.row())
        nodes = [self.remove(ind) for ind in indexesSorted]
        assert None not in nodes

        self.beginInsertRows(indexParent, firstNodeIndex, firstNodeIndex)
        mergedNode = nodeType(tagList=nodes, parent=nodeParent)
        for n in nodes:
            n.parent = mergedNode
        nodeParent.tagList.insert(firstNodeIndex, mergedNode)
        self.endInsertRows()

        return self.index(firstNodeIndex, 0, indexParent)

    def remove(self, curIndex: QModelIndex):
        if not curIndex.isValid() or curIndex == self.topLevelModel:
            return

        self.beginRemoveRows(curIndex.parent(), curIndex.row(), curIndex.row())
        node: TagFilterNode = curIndex.internalPointer()
        parentNode = node.parent
        assert isinstance(parentNode, TagFilterSequenceNode)
        parentNode.tagList.remove(node)
        node.parent = None
        self.endRemoveRows()
        return node
