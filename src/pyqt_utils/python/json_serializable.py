import json
import logging
from collections.abc import Callable, Sequence
from typing import Any

logger = logging.getLogger(__name__)
deepMapSequence = Sequence[None | type | Callable[[dict], Any]]


def fromJson(jsonStr: str, castTypes: deepMapSequence):
    if jsonStr == '' and castTypes and castTypes[0]:
        return castTypes[0]()

    rawObj = json.loads(jsonStr)
    return deepMap(rawObj, castTypes)


def deepMap(obj, mapElements: deepMapSequence):
    """Iterate map recursively.

    Iterate over elements and their sub-elements recursively and
    if element is `dict` and `mapElement` for that level is not None,
    then apply that `mapElement` to get mapped object.
    """
    if not mapElements:  # no more map elements - return original element
        return obj

    curMap, *otherMaps = mapElements
    if isinstance(obj, dict):
        if otherMaps:
            obj = {k: deepMap(v, otherMaps) for k, v in obj.items()}
        return obj if curMap is None else curMap(obj)

    try:
        return [deepMap(subObj, otherMaps) for subObj in obj]
    except AttributeError:
        return obj
