import logging
import traceback
import types
from collections.abc import Iterable
from pprint import pformat

logger = logging.getLogger(__name__)


class RemainingKwMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        try:
            return super().__new__(cls, name, bases, namespace, **kwargs)
        except TypeError as e:
            e.add_note(''.join(traceback.format_stack()))
            e.add_note(f"Not used {kwargs=}")
            raise


class ConflictHelperMeta(type):
    def __new__(cls, name, bases, namespace, **kwargs):
        try:
            return super().__new__(cls, name, bases, namespace, **kwargs)
        except TypeError as e:
            for note in cls.genMetaclassInfo(bases):
                e.add_note(note)
            raise

    @classmethod
    def genMetaclassInfo(cls, bases: Iterable[type]) -> Iterable[str]:
        for i, b in enumerate(bases):
            yield f"Base {i}: {b} with MRO:\n{pformat(type.mro(b))}"
            yield f"Meta {i}: {type(b)} with MRO:{type.mro(type(b))}"

    @classmethod
    def detectConflict(
        cls, *bases: type, metaclass=type, **kwargs
    ) -> tuple[type, type] | None:
        for i, b1 in enumerate(bases):
            for b2 in (object, *bases[i + 1 :]):
                try:
                    types.new_class(
                        'IsConflict',
                        (b1, b2),
                        {'metaclass': metaclass, **kwargs},
                    )
                except TypeError as e:
                    e.add_note(f"Metaclass: {metaclass} with MRO{type.mro(metaclass)}")
                    e.add_note(repr(e))
                    logger.exception("Cannot create class")
                    return b1, b2
        return None
