from collections.abc import Callable

type _Decorator[_BaseFun: Callable] = Callable[[_BaseFun], _BaseFun]

def changeStatusDec(
    *, msg: str = '', failureMsg: str = '', returnValue=True
) -> _Decorator: ...
