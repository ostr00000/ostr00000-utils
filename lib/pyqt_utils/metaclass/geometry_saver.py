from typing import Protocol, Any, runtime_checkable

from PyQt5.QtWidgets import QWidget, QDialog, QMainWindow
from decorator import decorator

from pyqt_utils.metaclass.base import BaseMeta


@runtime_checkable
class SettingProtocol(Protocol):
    def value(self, key: str, default: Any = None) -> Any: ...

    def setValue(self, key: str, value: Any): ...

    def sync(self): ...


@decorator
def saveGeometryDecFac(fun, key: str = None, settings: SettingProtocol = None,
                       *args, **kwargs):
    self: QWidget = args[0]
    settings.setValue(key, self.saveGeometry())
    settings.sync()
    return fun(*args, **kwargs)


@decorator
def loadGeometryDecFac(fun, key: str = None, settings: SettingProtocol = None,
                       *args, **kwargs):
    ret = fun(*args, **kwargs)
    geom = settings.value(key, None)
    if geom:
        self: QWidget = args[0]
        self.restoreGeometry(geom)
    return ret


@decorator
def saveStateDecFac(fun, key: str = None, settings: SettingProtocol = None,
                    *args, **kwargs):
    self: QMainWindow = args[0]
    settings.setValue(key, self.saveState())
    settings.sync()
    return fun(*args, **kwargs)


@decorator
def loadStateDecFac(fun, key: str = None, settings: SettingProtocol = None,
                    *args, **kwargs):
    ret = fun(*args, **kwargs)
    state = settings.value(key, None)
    if state:
        self: QMainWindow = args[0]
        self.restoreState(state)
    return ret


class GeometrySaverMeta(BaseMeta):
    def __new__(mcs, name, bases, attrs,
                settings: SettingProtocol = None,
                saveName: str = None):

        assert isinstance(settings, SettingProtocol), \
            "setting argument must be provided when class is created"
        assert any(issubclass(base, QWidget) for base in bases)
        if not saveName:
            saveName = name

        try:
            closeEvent = attrs['closeEvent']
        except KeyError:
            def closeEvent(self, event):
                return super(obj, self).closeEvent(event)

        try:
            __init__ = attrs['__init__']
        except KeyError:
            def __init__(self, *args, **kwargs):
                super(obj, self).__init__(*args, **kwargs)

        facAttr = {'key': f'geometry/{saveName}', 'settings': settings}
        saveGeometryDec = saveGeometryDecFac(**facAttr)
        attrs['closeEvent'] = saveGeometryDec(closeEvent)
        attrs['__init__'] = loadGeometryDecFac(**facAttr)(__init__)

        if QDialog in bases:
            try:
                accept = attrs['accept']
            except KeyError:
                def accept(self):
                    return super(obj, self).accept()

            attrs['accept'] = saveGeometryDec(accept)

        if QMainWindow in bases:
            facAttr['key'] = f'state/{saveName}'
            attrs['__init__'] = loadStateDecFac(**facAttr)(attrs['__init__'])
            attrs['closeEvent'] = saveStateDecFac(**facAttr)(attrs['closeEvent'])

        obj = super().__new__(mcs, name, bases, attrs)
        return obj
