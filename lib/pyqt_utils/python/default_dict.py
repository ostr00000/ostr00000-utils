from typing import TypeVar

T = TypeVar('T')


class DefaultDict(dict[str, T]):
    def __init__(self, defaultValue: T, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.defaultValue = defaultValue

    def __missing__(self, key) -> T:
        return self.defaultValue
