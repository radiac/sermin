"""
Util functions
"""
from subprocess import Popen, PIPE

from .exceptions import ShellError
from . import report


class ShellOutput(str):
    def __new__(cls, stdout, stderr):
        # Store raw
        stdout = stdout.strip() if stdout else ''
        stderr = stderr.strip() if stderr else ''

        # Join stdout and stderr
        value = stdout
        if stderr:
            if stdout:
                value += '\n'
            value += stderr

        self = super(ShellOutput, cls).__new__(cls, value)
        self.stdout = stdout
        self.stderr = stderr
        return self


def shell(cmd, expect_errors=False):
    """
    Perform a shell command

    Arguments:
        cmd     Shell command to execute

    Returns
        out     Output string
        out.stdout      The stdout
        out.stderr      The stderr
        out.return_code The return code
    """
    report.info('$ {}'.format(cmd), label='shell')

    process = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    out = ShellOutput(stdout, stderr)
    out.cmd = cmd
    out.return_code = process.returncode
    report.info(out, label='shell')

    if not expect_errors and out.return_code != 0:
        msg = 'Unexpected return code {code} from {cmd}: {out}'
        raise ShellError(msg.format(code=out.return_code, cmd=cmd, out=out))
    return out
