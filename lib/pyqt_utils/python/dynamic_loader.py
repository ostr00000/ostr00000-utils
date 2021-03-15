import importlib
import logging
import pkgutil
import traceback
from inspect import isabstract, isclass
from types import ModuleType
from typing import Iterator, Type

logger = logging.getLogger(__name__)


def loadClassFromPackage(
        package: ModuleType,
        requiredSubclass=type,
        filterPrivate=True,
) -> Iterator[Type]:
    """
    Load all modules from package and subpackages and return classes defined within.
    :param package: Main package from all classes will be loaded.
    :param requiredSubclass: Return only classes with this type.
    :param filterPrivate: Ignore all classes starting with '_' (underscore).
    :return:
    """
    for moduleInfo in pkgutil.walk_packages(
            package.__path__, prefix=package.__name__ + '.'):
        try:
            mod: ModuleType = importlib.import_module(moduleInfo.name)
        except Exception as exc:
            logger.error(str(exc))
            logger.debug(traceback.format_exc())
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
