from __future__ import annotations

import pickle
from collections.abc import Iterable


class TagFilterNode:
    TAG_NAME = ''

    def __init__(self, tagName: str = None, parent: TagFilterNode = None):
        self.tagName = self.TAG_NAME if tagName is None else tagName
        self.parent = parent

    def isAccepted(self, tags: list[str]) -> bool:
        return self.tagName in tags

    def filterTags(self, allowedTags: Iterable[str]):
        return self.tagName in allowedTags

    def __str__(self):
        return self.tagName

    @classmethod
    def deserialize(cls, data: bytes):
        return pickle.loads(data)

    def serialize(self) -> bytes:
        return pickle.dumps(self, protocol=0)

    def __len__(self):
        return 0


class TagFilterSequenceNode(TagFilterNode):
    def __init__(self, tagList: list[TagFilterNode] = (), parent: TagFilterNode = None):
        self.tagList = tagList
        super().__init__(parent=parent)

    def filterTags(self, allowedTags: Iterable[str]):
        self.tagList = [t for t in self.tagList if t.filterTags(allowedTags)]
        return bool(self.tagList)

    def __len__(self):
        return len(self.tagList)


class TagFilterOrNode(TagFilterSequenceNode):
    TAG_NAME = 'OR'

    def isAccepted(self, tags: list[str]) -> bool:
        return any(t.isAccepted(tags) for t in self.tagList)


class TagFilterAndNode(TagFilterSequenceNode):
    TAG_NAME = 'AND'

    def isAccepted(self, tags: list[str]) -> bool:
        return all(t.isAccepted(tags) for t in self.tagList)
