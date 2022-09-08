import copy
import logging

from PyQt5.QtCore import QModelIndex, QAbstractItemModel, Qt

from pyqt_utils.widgets.include_exclude.nodes import TagFilterNode, TagFilterSequenceNode, \
    TagFilterOrNode

logger = logging.getLogger(__name__)


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

        if (grandParentNode := parentNode.parent) is None:
            parentRow = 0
        else:
            assert isinstance(grandParentNode, TagFilterSequenceNode)
            parentRow = any(i for i, n in enumerate(grandParentNode.tagList)
                            if n == parentNode)

        return self.createIndex(parentRow, 0, parentNode)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return

        match role:
            case Qt.DisplayRole | Qt.ToolTipRole:
                data: TagFilterNode = index.internalPointer()
                return str(data)

    def addSimple(self, text: str, parent: QModelIndex):
        if parent.isValid():
            node = parent.internalPointer()
        else:
            node = self.topNode
            parent = self.topLevelModel

        if isinstance(node, TagFilterSequenceNode):
            for t in node.tagList:
                if t.tagName == text:
                    return

            row = len(node.tagList)
            self.beginInsertRows(parent, row, row)
            tn = TagFilterNode(tagName=text, parent=node)
            node.tagList.append(tn)
            self.endInsertRows()

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

        nodes = [self.remove(ind) for ind in indexes]
        assert None not in nodes

        self.beginInsertRows(indexParent, firstNodeIndex, firstNodeIndex + 1)
        mergedNode = nodeType(tagList=nodes, parent=nodeParent)
        for n in nodes:
            n.parent = mergedNode
        nodeParent.tagList.insert(firstNodeIndex, mergedNode)
        self.endInsertRows()

        return self.index(firstNodeIndex, 0, indexParent)

    def remove(self, curIndex: QModelIndex):
        if not curIndex.isValid() or curIndex == self.topLevelModel:
            return

        self.beginRemoveRows(curIndex.parent(), 0, 0)
        node: TagFilterNode = curIndex.internalPointer()
        parentNode = node.parent
        assert isinstance(parentNode, TagFilterSequenceNode)
        parentNode.tagList.remove(node)
        self.endRemoveRows()
        return node
