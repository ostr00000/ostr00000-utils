from __future__ import annotations

import pickle
from collections.abc import Iterable
from typing import Protocol, Self


class StrComparable(Protocol):
    def __eq__(self, other: str):
        ...


class TagFilterNode:
    TAG_NAME = ''

    def __init__(self, tagName: str = None, parent: TagFilterNode = None):
        self.tagName = self.TAG_NAME if tagName is None else tagName
        self.parent = parent

    def isAccepted(self, tags: list[StrComparable | str]) -> bool:
        return self.tagName in tags

    def filterTags(self, allowedTags: Iterable[str]):
        return self.tagName in allowedTags

    def __str__(self):
        return self.tagName

    def __repr__(self):
        return str(self)

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        return pickle.loads(data)

    def serialize(self) -> bytes:
        return pickle.dumps(self, protocol=0)

    def __len__(self):
        return 0


class TagFilterSequenceNode(TagFilterNode):
    def __init__(self, tagList: list[TagFilterNode] = None, parent: TagFilterNode = None):
        self.tagList = [] if tagList is None else tagList
        super().__init__(parent=parent)
        for t in self.tagList:
            t.parent = self

    def filterTags(self, allowedTags: Iterable[str]):
        self.tagList = [t for t in self.tagList if t.filterTags(allowedTags)]
        return bool(self.tagList)

    def insert(self, pos: int, node: TagFilterNode):
        self.tagList.insert(pos, node)
        node.parent = self

    def remove(self, node: TagFilterNode):
        self.tagList.remove(node)
        node.parent = None

    def __repr__(self):
        return f'{str(self)}[{",".join(repr(t) for t in self.tagList)}]'

    def __len__(self):
        return len(self.tagList)


class TagFilterOrNode(TagFilterSequenceNode):
    TAG_NAME = 'OR'

    def isAccepted(self, tags: list[str]) -> bool:
        return any(t.isAccepted(tags) for t in self.tagList)


class TagFilterExcludeNode(TagFilterSequenceNode):
    TAG_NAME = 'NOT'

    def __init__(self, tagContent: TagFilterNode, parent: TagFilterNode = None):
        super().__init__([tagContent], parent=parent)

    def isAccepted(self, tags: list[str]) -> bool:
        return not super().isAccepted(tags)

    @property
    def content(self):
        assert len(self.tagList) == 1
        return self.tagList[0]


class TagFilterAndNode(TagFilterSequenceNode):
    TAG_NAME = 'AND'

    def isAccepted(self, tags: list[str]) -> bool:
        return all(t.isAccepted(tags) for t in self.tagList)
