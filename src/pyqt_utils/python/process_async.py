import ctypes
import logging
import re
import shlex
import signal
from collections.abc import Callable, Iterable
from functools import wraps
from pathlib import Path
from subprocess import PIPE, Popen
from threading import Thread
from typing import overload

logger = logging.getLogger(__name__)
type StrPopen = Popen[str]


def createPreExecForParentDeath(sig=signal.SIGTERM):
    """Ensure child process exit when parent process exits.

    Based on:
    https://stackoverflow.com/a/43152455
    https://man7.org/linux/man-pages/man2/prctl.2.html

    Example:
    >>> import subprocess
    >>> subprocess.Popen(['sleep', 10], preexec_fn=createPreExecForParentDeath())
    """
    PR_SET_PDEATHSIG = 1

    def preExec():
        return ctypes.CDLL("libc.so.6").prctl(PR_SET_PDEATHSIG, sig)

    return preExec


@wraps(Popen.__init__)
def openProcessWrapper(*args, shell=False, **kwargs) -> StrPopen:
    logger.info(f"Run command {args}")
    # SKIP: this may be configured by user, so there is indeed some kind of risk
    process: StrPopen = Popen(  # noqa: S603 # SKIP
        *args,
        shell=shell,
        stdout=PIPE,
        stderr=PIPE,
        encoding='UTF-8',
        text=True,
        **kwargs,
    )

    match process.args:
        case str(strArgs):
            pass
        case Path() as pathArg:
            strArgs = str(pathArg)
        case list(listArgs):
            strArgs = shlex.join([str(s) for s in listArgs])
        case _:
            msg = f"Unexpected type of process.args: {type(process.args)}"
            raise TypeError(msg)

    logger.info(strArgs)
    return process


class OutputReader:
    def __init__(self, process: StrPopen, **kwargs):
        self.originalProcess = process
        self.outputThread = self._startThread(process, target=self._readOutput)
        self.stderrThread = self._startThread(process, target=self._readError)

    @classmethod
    def _startThread(cls, process: StrPopen, target: Callable[[StrPopen], None]):
        th = Thread(
            target=target,
            name=f"{process.args}.{target.__name__}",
            args=(process,),
        )
        th.daemon = True
        th.start()
        return th

    def _readOutput(self, process: StrPopen):
        if process.stdout is None:
            return

        for line in process.stdout.readlines():
            if not (strippedLine := line.strip()):
                continue
            self.processOutput(strippedLine)

    def processOutput(self, line: str):
        pass

    def _readError(self, process: StrPopen):
        if process.stderr is None:
            return

        for line in process.stderr.readlines():
            if not (strippedLine := line.strip()):
                continue
            self.processError(strippedLine)

    def processError(self, line: str):
        pass


class OutputReaderLogger(OutputReader):
    def __init__(
        self, process: StrPopen, logHandlers: Iterable[logging.Handler] = (), **kwargs
    ):
        self.log = logging.getLogger(f'{__name__}.{type(self).__name__}.{process.pid}')
        self.log.setLevel(logging.DEBUG)
        for h in list(self.log.handlers):
            self.log.removeHandler(h)
        for h in logHandlers:
            self.log.addHandler(h)

        super().__init__(process, **kwargs)

    def _readOutput(self, process: StrPopen):
        super()._readOutput(process)
        self.log.info(f"Process finished {process.pid=} {process.returncode=}")

    def processOutput(self, line: str):
        self.log.debug(line)

    def processError(self, line: str):
        self.log.error(line)


class PermissionFixReader(OutputReaderLogger):
    PERMISSION_DENIED = re.compile('(?:[^:]+:)* ?([^:]+): Permission denied')
    """Tested patterns:
    /bin/sh: 1: ./script.sh: Permission denied
    """

    def processError(self, line: str):
        if (match := self.PERMISSION_DENIED.match(line)) is None:
            return

        if (fileWithoutPermission := match.group(1)) is None:
            self.log.error("Cannot find file from pattern")
            return

        if (workingDir := self._getWorkingDir()) is None:
            workingDir = Path(fileWithoutPermission).parent

        self._fixPermission(f'cd "{workingDir}" ; chmod u+x "{fileWithoutPermission}"')

        process = openProcessWrapper(self.originalProcess.args)
        self.outputThread = self._startThread(process, target=self._readOutput)
        self.stderrThread = self._startThread(process, target=self._readError)

    def _getWorkingDir(self) -> str | None:
        match self.originalProcess.args:
            case str(orgArg):
                orgArgs = shlex.split(orgArg)
            case [*orgArgs]:
                pass
            case _:
                self.log.error("Unknown type for input arguments")
                return None

        match orgArgs:
            case ['cd', workingDir, _rest]:
                return str(workingDir)

            case [_notCd, _workingDir, _rest]:
                self.log.error("Command do not start with `cd` command")
                return None

            case _:
                self.log.error("Cannot parse command")
                return None

    def _fixPermission(self, cmd: str):
        permissionProcess = openProcessWrapper(cmd, shell=True)  # noqa: S604
        stdout, stderr = permissionProcess.communicate()
        if stderr:
            self.log.error(stderr)
        if stdout:
            self.log.info(stdout)


@overload
def runProcessAsync(
    cmd: list[str],
    *args,
    shell=False,
    logHandlers: Iterable[logging.Handler] = (),
    reader: type[OutputReader] | None = PermissionFixReader,
    **kwargs,
): ...


@overload
def runProcessAsync(
    cmd: str,
    *args,
    shell=True,
    logHandlers: Iterable[logging.Handler] = (),
    reader: type[OutputReader] | None = PermissionFixReader,
    **kwargs,
): ...


def runProcessAsync(
    cmd: str | list[str],
    *args,
    shell=True,
    logHandlers: Iterable[logging.Handler] = (),
    reader: type[OutputReader] | None = PermissionFixReader,
    **kwargs,
):
    if not cmd:
        return False

    try:
        process = openProcessWrapper(cmd, *args, shell=shell, **kwargs)
    except Exception:
        logger.exception("Error when running process")
        return False

    if reader:
        reader(process, logHandlers=logHandlers)

    return True
