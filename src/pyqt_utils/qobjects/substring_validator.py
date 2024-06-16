from collections.abc import Iterable

from PyQt5.QtGui import QValidator


class SubstringValidator(QValidator):
    def __init__(self, possibleValues: Iterable[str] = (), parent=None):
        super().__init__(parent)
        self._possibleValues: list[str] = []
        self.setPossibleValues(possibleValues)

    def setPossibleValues(self, possibleValues: Iterable[str] = ()):
        self._possibleValues = list(possibleValues)

    def validate(self, inputText: str, pos: int):
        if inputText in self._possibleValues:
            return QValidator.Acceptable, inputText, pos

        if self._getRemainingOptions(inputText):
            return QValidator.Intermediate, inputText, pos

        return QValidator.Invalid, inputText, pos

    def fixup(self, inputText: str) -> str:
        match self._getRemainingOptions(inputText):
            case [onlyOne]:
                return onlyOne
            case _:
                return inputText

    def _getRemainingOptions(self, inputText: str) -> list[str]:
        size = len(inputText)
        return [p for p in self._possibleValues if p[:size] == inputText]
