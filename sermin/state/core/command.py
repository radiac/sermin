"""
Execute command
"""
from future.utils import python_2_unicode_compatible

from ...utils import shell
from ..base import State


@python_2_unicode_compatible
class Command(State):
    def __init__(self, command, cwd=None, **kwargs):
        self.command = command
        self.cwd = cwd
        super(Command, self).__init__(**kwargs)

    def __str__(self):
        return self.command

    def check(self):
        return False

    def apply(self):
        if self.cwd:
            self.report.info('Changing dir and running command')
            shell(self.command, cd=self.cwd)
        else:
            self.report.info('Running command')
            shell(self.command)
