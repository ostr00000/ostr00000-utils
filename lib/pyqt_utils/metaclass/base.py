from abc import ABCMeta
from typing import Type

from PyQt5.QtCore import QObject


class BaseMeta(type):
    @classmethod
    def wrap(mcs, otherClass: Type):
        return mcs.wrapMetaClass(type(otherClass))

    @classmethod
    def wrapMetaClass(mcs, otherMetaClass):
        class Wrapper(mcs, otherMetaClass):
            pass

        return Wrapper


class QtMeta(BaseMeta, type(QObject)):
    pass


class QtAbcMeta(ABCMeta, QtMeta):
    pass
