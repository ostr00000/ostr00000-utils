from collections.abc import Callable, Sequence
from functools import wraps
from os import PathLike
from typing import Any, Concatenate, cast

type StrPath = str | PathLike[str]
type MethodT[**P, R] = Callable[Concatenate[Any, P], R]


def wrapAnnotation[
    **P, R
](
    wrapped: MethodT[P, R],
    assigned: Sequence[str] = ('__annotations__',),
    updated: Sequence[str] = (),
) -> Callable[[MethodT[P, R]], MethodT[P, R]]:
    """Wrap similar to `functools.wrap`, but allows to type-check methods.

    This is especially useful when decorating __init__ from base class signature.
    Based on:
    https://github.com/microsoft/pyright/discussions/4426#discussioncomment-4642685
    """
    return cast(
        Callable[[MethodT[P, R]], MethodT[P, R]],
        wraps(wrapped, assigned, updated),
    )
