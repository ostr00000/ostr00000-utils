import logging
import re
import shlex
from subprocess import Popen, STDOUT, PIPE
from threading import Thread
from typing import Optional, Union, List, Type

logger = logging.getLogger(__name__)


def _PopenWrapper(*args, shell=True, **kwargs):
    logger.info(f"Run command {args}")
    process = Popen(*args, shell=shell, stdout=PIPE, stderr=STDOUT, encoding='UTF-8', **kwargs)
    logger.info(shlex.join(process.args) if isinstance(process.args, list) else process.args)
    return process


class OutputReader:
    def __init__(self, process: Popen):
        self.log = logging.getLogger(f'{__name__}.{type(self).__name__}.{process.pid}')
        self.log.setLevel(logging.DEBUG)

        self.originalProcess = process
        self._startThread(process)

    def _startThread(self, process: Popen):
        th = Thread(target=self._readOutput, name=f"{process.args}", args=(process,))
        th.daemon = True
        th.start()

    def _readOutput(self, process: Popen):
        for line in process.stdout.readlines():
            line = line.strip()
            if not line:
                continue

            self.log.debug(line)
            self.processOutput(line)

        self.log.info(f"Proces finished {process.pid}")

    def processOutput(self, line: str):
        pass


class PermissionFixReader(OutputReader):
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
        self._startThread(_PopenWrapper(self.originalProcess.args))

    def _getWorkingDir(self) -> Optional[str]:
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


def runProcessAsync(cmd: Union[None, str, List[str]], *args, shell=True,
                    reader: Optional[Type[OutputReader]] = PermissionFixReader, **kwargs):
    if not cmd:
        return False

    try:
        process = _PopenWrapper(cmd, *args, shell, **kwargs)
    except Exception as e:
        logger.error(str(e))
        return False

    if reader:
        reader(process)

    return True
