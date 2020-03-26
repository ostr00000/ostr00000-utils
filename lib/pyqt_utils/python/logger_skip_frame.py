import logging


class SkipFrameInModule(object):
    def __init__(self, *args):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        self._moduleNames = [logging._srcfile] + list(args)
        logging._srcfile = self

    def addModule(self, moduleName):
        """Expected argument: __file__ """
        self._moduleNames.append(moduleName)

    def __eq__(self, other):
        """Skip also decorators from decorator package"""
        return other in self._moduleNames or other.startswith('<decorator-gen-')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="[%(filename)-16s:%(lineno)-3d] %(message)s")

    logging.info("Known filename")
    skipFrame = SkipFrameInModule(__file__)
    logging.info("Unknown filename")
