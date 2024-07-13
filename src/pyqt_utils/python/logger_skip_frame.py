import logging


class SkipFrameInModule:
    def __init__(self, *args):
        # SKIP reason: This is the only way, because there is no public API
        # noinspection PyUnresolvedReferences,PyProtectedMember
        self._moduleNames = [logging._srcfile, *args]  # noqa: SLF001 # SKIP
        logging._srcfile = self  # noqa: SLF001 # SKIP

    def addModule(self, moduleName):
        """Add a module to the ignored modules in logging module.

        Expected call:
        >>> sf = SkipFrameInModule()
        >>> sf.addModule(__file__)
        """
        self._moduleNames.append(moduleName)

    def __eq__(self, other):
        """Skip also decorators from decorator package."""
        return other in self._moduleNames or other.startswith('<decorator-gen-')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO, format="[%(filename)-16s:%(lineno)-3d] %(message)s"
    )

    logging.info("Known filename")
    skipFrame = SkipFrameInModule(__file__)
    logging.info("Unknown filename")
