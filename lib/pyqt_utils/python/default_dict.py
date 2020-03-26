from typing import TypeVar, Dict

T = TypeVar('T')


class DefaultDict(dict, Dict[str, T]):
    def __init__(self, defaultValue: T, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultValue = defaultValue

    def __missing__(self, key) -> T:
        return self.defaultValue
