import importlib
import logging
import pkgutil
from collections.abc import Iterator
from inspect import isabstract, isclass
from types import ModuleType

_moduleLogger = logging.getLogger(__name__)


def loadClassFromPackage[T](
    package: ModuleType,
    *,
    requiredSubclass: type[T] = object,
    filterPrivate: bool = True,
    logger: logging.Logger = _moduleLogger,
) -> Iterator[type[T]]:
    """
    Load all modules from package and subpackages and return classes defined within.

    :param package: Main package from all classes will be loaded.
    :param requiredSubclass: Return only classes with this type.
    :param filterPrivate: Ignore all classes starting with '_' (underscore).
    :param logger: Logger to inform about success or failure.
    :return: Iterator with classes defined within package.
    """
    for moduleInfo in pkgutil.walk_packages(
        package.__path__, prefix=package.__name__ + '.'
    ):
        try:
            mod: ModuleType = importlib.import_module(moduleInfo.name)
        except SyntaxError:
            raise
        except Exception:
            msg = f"Error when loading module {moduleInfo.name}"
            logger.exception(msg)
            continue

        for name, maybeClass in mod.__dict__.items():
            if filterPrivate and name.startswith('_'):
                continue
            if not isclass(maybeClass):
                continue
            if isabstract(maybeClass):
                continue
            if maybeClass.__module__ != moduleInfo.name:
                continue
            if not issubclass(maybeClass, requiredSubclass):
                continue

            logger.debug(f"Found {maybeClass}")
            yield maybeClass
