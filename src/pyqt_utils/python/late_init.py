import logging
from typing import Self, overload

logger = logging.getLogger(__name__)


class LateInit[T]:
    """
    Descriptor for attribute not initialized in __init__.

    This descriptor must be accessed after its connected private value is initialized.
    The connected private value should have same name as this descriptor,
    but with additional prefix `_`.
    You may also choose different name in descriptor init.

    Example:
    >>> class A:
    ...    text = LateInit[str]()
    ...    myInt = LateInit[int]('_count')
    ...    _count = 0
    ...
    ...    def __init__(self):
    ...        self._text: str | None = None
    ...
    ...    def initializeText(self, text: str):
    ...        self._text = text
    ...
    ...        assert self._count == 0
    ...        assert self.myInt == 0
    ...        self._count = 13
    ...        assert self._count == 13
    ...        assert self.myInt == 13
    ...
    ...    def run(self):
    ...        assert isinstance(self.text, str)
    >>> a = A()
    >>> a.initializeText("My new text")
    >>> a.run()
    """

    def __init__(self, name: str = '', *, errorMsg: str = ''):
        self._name = name
        self._errorMsg = errorMsg

    def __set_name__(self, _owner, name):
        if not self._name:
            self._name = f'_{name}'

    @overload
    def __get__(self, instance: None, _owner) -> Self: ...

    @overload
    def __get__(self, instance, _owner) -> T: ...

    def __get__(self, instance, _owner):
        if instance is None:
            return self

        try:
            val = getattr(instance, self._name)
        except AttributeError as ae:
            msg = (
                f"{instance=} does not have late initialized "
                f"attribute `{self._name}`, but the attribute is accessed."
            )
            if self._errorMsg:
                msg = f'{msg} {self._errorMsg}'
            raise AttributeError(msg) from ae

        if val is None:
            msg = (
                f"{instance=} have attribute `{self._name}`,"
                f" but it is not initialized (has `None`)."
            )
            if self._errorMsg:
                msg = f'{msg} {self._errorMsg}'
            raise AttributeError(msg)

        return val

    def __set__(self, instance, value: T | None):
        setattr(instance, self._name, value)

    def __delete__(self, instance):
        setattr(instance, self._name, None)
