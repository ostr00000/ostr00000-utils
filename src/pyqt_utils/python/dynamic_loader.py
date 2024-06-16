import importlib
import logging
import pkgutil
from inspect import isabstract, isclass
from types import ModuleType
from typing import Iterator, TypeVar

_moduleLogger = logging.getLogger(__name__)
_T = TypeVar('_T')


def loadClassFromPackage(
    package: ModuleType,
    *,
    requiredSubclass: type[_T] = object,
    filterPrivate: bool = True,
    logger: logging.Logger = _moduleLogger,
) -> Iterator[type[_T]]:
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
        except Exception as exc:
            logger.exception(exc)
        else:
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
