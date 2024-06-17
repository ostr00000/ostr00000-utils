from typing import TYPE_CHECKING, Any, Protocol, cast, runtime_checkable

from decorator import decorator

if TYPE_CHECKING:
    from PyQt5.QtWidgets import QMainWindow, QWidget

_reqKwarg: Any = None


@runtime_checkable
class SettingProtocol(Protocol):
    # SKIP: false positive, https://github.com/jendrikseipp/vulture/issues/309
    def value(self, key: str, default: Any = None) -> Any: ...  # noqa: F841

    def setValue(self, key: str, value: Any): ...

    def sync(self): ...


@decorator
def saveGeometryDecFac(
    fun, key: str = _reqKwarg, settings: SettingProtocol = _reqKwarg, *args, **kwargs
):
    self: QWidget = args[0]
    settings.setValue(key, self.saveGeometry())
    settings.sync()
    return fun(*args, **kwargs)


@decorator
def loadGeometryDecFac(
    fun, key: str = _reqKwarg, settings: SettingProtocol = _reqKwarg, *args, **kwargs
):
    ret = fun(*args, **kwargs)
    if geom := settings.value(key, None):
        self: QWidget = args[0]
        self.restoreGeometry(geom)
    return ret


@decorator
def saveStateDecFac(
    fun, key: str = _reqKwarg, settings: SettingProtocol = _reqKwarg, *args, **kwargs
):
    self: QMainWindow = args[0]
    settings.setValue(key, self.saveState())
    settings.sync()
    return fun(*args, **kwargs)


@decorator
def loadStateDecFac(
    fun, key: str = _reqKwarg, settings: SettingProtocol = _reqKwarg, *args, **kwargs
):
    ret = fun(*args, **kwargs)
    if state := settings.value(key, None):
        self: QMainWindow = args[0]
        self.restoreState(state)
    return ret
