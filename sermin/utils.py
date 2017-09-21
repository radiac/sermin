"""
Util functions
"""
import os
import shlex
from subprocess import Popen, PIPE

from six import string_types

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


def shell(cmd, cd=None, expect_errors=False):
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
    cmd_display = cmd
    if not isinstance(cmd, string_types):
        cmd_display = ' '.join(cmd)

    if isinstance(cmd, string_types):
        cmd = shlex.split(cmd)

    old_dir = os.getcwd()
    if cd:
        report.info('$ cd {}'.format(cd))
        os.chdir(cd)

    report.info('$ {}'.format(cmd_display), label='shell')
    process = Popen(cmd, shell=False, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    out = ShellOutput(stdout, stderr)
    out.cmd = cmd
    out.return_code = process.returncode
    report.info(out, label='shell')

    if cd:
        os.chdir(old_dir)

    if not expect_errors and out.return_code != 0:
        msg = 'Unexpected return code {code} from {cmd}: {out}'
        raise ShellError(msg.format(
            code=out.return_code,
            cmd=cmd_display,
            out=out,
        ))
    return out
