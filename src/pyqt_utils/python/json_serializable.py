import json
import logging
from typing import Sequence, Callable, Any

logger = logging.getLogger(__name__)
deepMapElement = None | type | Callable[[dict], Any]
deepMapSequence = Sequence[deepMapElement]


def fromJson(jsonStr: str, castTypes: deepMapSequence):
    if jsonStr == '' and castTypes and castTypes[0]:
        return castTypes[0]()

    rawObj = json.loads(jsonStr)
    return deepMap(rawObj, castTypes)


def deepMap(obj, mapElements: deepMapSequence):
    """Iterate over elements and their sub-elements recursively and
    if element is dict and mapElement for that level is not Node
    then apply that mapElement to get mapped object."""
    if not mapElements:  # no more map elements - return original element
        return obj
    else:
        curMap, *otherMaps = mapElements

    if isinstance(obj, dict):
        if otherMaps:
            obj = {k: deepMap(v, otherMaps) for k, v in obj.items()}
        if curMap is not None:
            return curMap(obj)
    else:
        try:
            return [deepMap(subObj, otherMaps) for subObj in obj]
        except AttributeError:
            pass

    return obj
