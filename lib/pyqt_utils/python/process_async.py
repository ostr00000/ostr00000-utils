import logging
import re
import shlex
from subprocess import Popen, PIPE
from threading import Thread
from typing import Callable, overload

logger = logging.getLogger(__name__)


def _PopenWrapper(*args, shell=True, **kwargs):
    logger.info(f"Run command {args}")
    process = Popen(*args, shell=shell, stdout=PIPE, stderr=PIPE, encoding='UTF-8', **kwargs)
    logger.info(shlex.join(process.args) if isinstance(process.args, list) else process.args)
    return process


class OutputReader:
    def __init__(self, process: Popen, **kwargs):
        self.originalProcess = process
        self.outputThread = self._startThread(process, target=self._readOutput)
        self.stderrThread = self._startThread(process, target=self._readError)

    @staticmethod
    def _startThread(process: Popen, target: Callable[[Popen], None]):
        th = Thread(target=target, name=f"{process.args}.{target.__name__}", args=(process,))
        th.daemon = True
        th.start()
        return th

    def _readOutput(self, process: Popen):
        for line in process.stdout.readlines():
            line = line.strip()
            if not line:
                continue
            self.processOutput(line)

    def processOutput(self, line: str):
        pass

    def _readError(self, process: Popen):
        for line in process.stderr.readlines():
            line = line.strip()
            if not line:
                continue
            self.processError(line)

    def processError(self, line: str):
        pass


class OutputReaderLogger(OutputReader):
    def __init__(self, process: Popen, logHandlers: list[logging.Handler] = (), **kwargs):
        super().__init__(process, **kwargs)
        self.log = logging.getLogger(f'{__name__}.{type(self).__name__}.{process.pid}')
        self.log.setLevel(logging.DEBUG)
        for h in logHandlers:
            self.log.addHandler(h)

    def _readOutput(self, process: Popen):
        super()._readOutput(process)
        self.log.info(f"Proces finished {process.pid=} {process.returncode=}")

    def processOutput(self, line: str):
        self.log.debug(line)

    def processError(self, line: str):
        self.log.error(line)


class PermissionFixReader(OutputReaderLogger):
    PERMISSION_DENIED = re.compile('(?:[^:]+:)* ?([^:]+): Permission denied')
    """Tested patterns:
    /bin/sh: 1: ./script.sh: Permission denied
    """

    def processOutput(self, line: str):
        if (match := self.PERMISSION_DENIED.match(line)) is None:
            return

        if (fileWithoutPermission := match.group(1)) is None:
            self.log.error("Cannot find file from pattern")
            return

        if (workingDir := self._getWorkingDir()) is None:
            self.log.error("Cannot find working dir")
            return

        self._fixPermission(f'cd "{workingDir}" ; chmod u+x "{fileWithoutPermission}"')

        process = _PopenWrapper(self.originalProcess.args)
        self.outputThread = self._startThread(process, target=self._readOutput)
        self.stderrThread = self._startThread(process, target=self._readError)

    def _getWorkingDir(self) -> str | None:
        args = shlex.split(self.originalProcess.args)

        if len(args) < 3:
            self.log.error("Cannot parse command")
            return None

        if args[0] != 'cd':
            self.log.error("Command do not contain 'cd'")
            return None

        return args[1]

    def _fixPermission(self, cmd: str):
        permissionProcess = _PopenWrapper(cmd)
        stdout, stderr = permissionProcess.communicate()
        if stderr:
            self.log.error(stderr)
        if stdout:
            self.log.info(stdout)


@overload
def runProcessAsync(cmd: list[str], *args, shell=False,
                    logHandlers: list[logging.Handler] = (),
                    reader: type[OutputReader] | None = PermissionFixReader, **kwargs):
    ...


def runProcessAsync(cmd: str, *args, shell=True,
                    logHandlers: list[logging.Handler] = (),
                    reader: type[OutputReader] | None = PermissionFixReader, **kwargs):
    if not cmd:
        return False

    try:
        process = _PopenWrapper(cmd, *args, shell=shell, **kwargs)
    except Exception as e:
        logger.error(str(e))
        return False

    if reader:
        reader(process, logHandlers=logHandlers)

    return True
