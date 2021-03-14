import importlib
import logging
import pkgutil
import traceback
from inspect import isabstract, isclass
from types import ModuleType
from typing import Iterator, Type

logger = logging.getLogger(__name__)


def loadClassFromPackage(package: ModuleType) -> Iterator[Type]:
    for moduleInfo in pkgutil.walk_packages(
            package.__path__, prefix=package.__name__ + '.'):
        try:
            mod: ModuleType = importlib.import_module(moduleInfo.name)
        except Exception as exc:
            logger.error(str(exc))
            logger.debug(traceback.format_exc())
        else:
            for name, maybeClass in mod.__dict__.items():
                if name.startswith('_'):
                    continue

                if isclass(maybeClass) and not isabstract(maybeClass):
                    if maybeClass.__module__ == moduleInfo.name:
                        logger.debug(f"Found {maybeClass}")
                        yield maybeClass
