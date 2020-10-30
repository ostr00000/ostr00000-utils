from typing import Type


class BaseMeta(type):
    @classmethod
    def wrap(mcs, otherClass: Type):
        return mcs.wrapMetaClass(type(otherClass))

    @classmethod
    def wrapMetaClass(mcs, otherMetaClass):
        class Wrapper(mcs, otherMetaClass):
            pass

        return Wrapper
