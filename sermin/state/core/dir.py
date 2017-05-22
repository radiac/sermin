"""
Directory management
"""
from future.utils import python_2_unicode_compatible
import os

from ..base import State


@python_2_unicode_compatible
class Dir(State):
    # States
    EXISTS = 'exist'
    ABSENT = 'absent'

    def __init__(self, path, state=EXISTS, **kwargs):
        super(Dir, self).__init__(**kwargs)
        self.path = path
        self.state = state

        # TODO: Ownership
        # TODO: Permissions

    def __str__(self):
        return self.path

    def exists(self):
        if os.path.exists(self.path):
            if os.path.isdir(self.path):
                return True
            else:
                raise ValueError('Expected directory is not a directory')
        return False

    def check(self):
        if self.exists():
            if self.state == self.EXISTS:
                self.report.debug('Already exists')
                return True
            self.report.debug('Does not exist but should')
            return False
        else:
            if self.state == self.ABSENT:
                self.report.debug('Does not exist')
                return True
            self.report.debug('Exists but should not')
            return False

    def apply(self):
        if self.exists():
            if self.state == self.ABSENT:
                self.report.info('Removing')
                os.rmdir(self.path)
        else:
            if self.state == self.EXISTS:
                self.report.info('Creating')
                os.makedirs(self.path)
