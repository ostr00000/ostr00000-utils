import inspect
import logging
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from types import FrameType, ModuleType

from PyQt5.QtWidgets import QWidget

from pyqt_utils.metaclass.qt_meta import AbcQtMeta

logger = logging.getLogger(__name__)


@contextmanager
def systemProfileContext(profileFunc):
    oldProfile = sys.getprofile()
    try:
        sys.setprofile(profileFunc)
        yield
    finally:
        sys.setprofile(oldProfile)


class MissingSuperCall(Exception):
    pass


class BaseWidget(QWidget, ABC, metaclass=AbcQtMeta):
    """Helper class for Qt generated class from `.ui` files.

    This class call `setupUi` and `retranslateUi` method.

    Example:
    >>> from PyQt5.QtWidgets import QDialog, QToolButton
    >>>
    >>> class MyAbstractDialog(QDialog, BaseUiWidget, ABC):
    ...     "Valid class order for an abstract class."
    >>>
    >>> class Ui_MyDialog:
    ...    "This class is generated by pyuic."
    ...     def setupUi(self, other): ...
    ...     def retranslateUi(self, other): ...
    >>>
    >>> class MyDialog(Ui_MyDialog, QDialog, BaseUiWidget):
    ...     "Valid class order for a concrete class."
    ...     def __pre_setup__(self, *args, **kwargs):
    ...        super().__pre_setup__(*args, **kwargs)
    ...        self.specialWidget = QToolButton(self)
    ...
    ...     def __post_init__(self, *args, **kwargs):
    ...        super().__post_init__(*args, **kwargs)
    ...        self.specialWidget.triggered.connect(self.onSpecialWidgetTriggered)
    ...
    ...     def onSpecialWidgetTriggered(self):
    ...        ...
    """

    def __init__(self, parent=None, *args, **kwargs):
        self.__forceSuperCall(self.__pre_init__, *args, **kwargs)
        super().__init__(parent=parent)
        self.__forceSuperCall(self.__pre_setup__, *args, **kwargs)
        self.__forceSuperCall(self.__post_init__, *args, **kwargs)

    def __forceSuperCall(self, method, *args, **kwargs):
        visitedClasses = []
        codeToClass = {
            expectedMethod.__code__: c
            for c in type(self).__mro__
            if (expectedMethod := c.__dict__.get(method.__name__))
        }

        def profileFunc(frame: FrameType, event: str, _arg):
            if event == 'call' and (curClass := codeToClass.get(frame.f_code)):
                visitedClasses.append(curClass)

        with systemProfileContext(profileFunc):
            method(*args, **kwargs)

        if not getattr(self, method.__name__ + 'executed__', False):
            cl = list(codeToClass.values())[len(visitedClasses) - 1]
            mod = inspect.getmodule(cl)
            modFile = mod.__file__ if isinstance(mod, ModuleType) else '!UnknownModule!'
            msg = (
                f'Need to call `super().{method.__name__}(*args, **kwargs)`\n'
                f'in overridden method: `{method.__name__}` in class: '
                f'`{cl.__module__}.{cl.__qualname__}`\n '
                f'in file {modFile}:1'
            )
            raise MissingSuperCall(msg)

    def __pre_init__(self, *args, **kwargs):
        """Initialize only pure python code."""
        self.__pre_init__executed__ = True

    def __pre_setup__(self, *args, **kwargs):
        """Initialize qt objects as attributes, self may be passed as parent."""
        self.__pre_setup__executed__ = True

    def __post_init__(self, *args, **kwargs):
        """Connect signals, create advanced objects that use element from ui."""
        self.__post_init__executed__ = True


class AbcUiWidget(ABC):
    @abstractmethod
    def setupUi(self, widget: QWidget):
        raise NotImplementedError

    @abstractmethod
    def retranslateUi(self, widget: QWidget):
        raise NotImplementedError


class BaseUiWidget(AbcUiWidget, BaseWidget, ABC):
    def __pre_setup__(self, *args, **kwargs):
        super().__pre_setup__(*args, **kwargs)
        self.setupUi(self)
        self.retranslateUi(self)
