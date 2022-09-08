from PyQt5.QtGui import QValidator


class SubstringValidator(QValidator):
    def __init__(self, possibleValues: list[str] = (), parent=None):
        super().__init__(parent)
        self.possibleValues = list(possibleValues)

    def validate(self, inputText: str, pos: int):
        if inputText in self.possibleValues:
            return QValidator.Acceptable, inputText, pos

        if self._getRemainingOptions(inputText):
            return QValidator.Intermediate, inputText, pos

        return QValidator.Invalid, inputText, pos

    def fixup(self, inputText: str) -> str:
        remaining = self._getRemainingOptions(inputText)
        if len(remaining) == 1:
            return remaining[0]
        else:
            return inputText

    def _getRemainingOptions(self, inputText: str):
        size = len(inputText)
        remainingOptions = []
        for p in self.possibleValues:
            if p[:size] == inputText:
                remainingOptions.append(p)
        return remainingOptions
