"""
User group management
"""
from future.utils import python_2_unicode_compatible

from ...utils import shell
from ..base import State


@python_2_unicode_compatible
class Group(State):
    """
    Group state
    """
    # States
    EXISTS = 'exist'
    ABSENT = 'absent'

    def __init__(self, name, state=EXISTS, gid=None, **kwargs):
        super(Group, self).__init__(**kwargs)
        self.name = name
        self.state = state
        self.gid = gid

    def __str__(self):
        return '{name} ({gid})'.format(
            name=self.name,
            gid=self.gid or self.get_gid() or '-',
        )

    def get_gid(self):
        ent = shell('getent group {}'.format(self.name), expect_errors=True)
        if not ent:
            return None
        return ent.split(':')[-2]

    def check(self):
        self.report.debug('checking')
        gid = self.get_gid()
        self.report.debug('gid {}'.format(gid))
        if gid:
            if self.state == self.EXISTS:
                self.report.debug('Already exists')
                if self.gid and self.gid != gid:
                    raise ValueError('Group gid does not match system')
                return True
            return False
        else:
            if self.state == self.ABSENT:
                self.report.debug('Does not exist')
                return True
            self.report.debug('Exists but should not')

            # TODO: Check that the group is empty - can't delete without

            return False

    def apply(self):
        gid = self.get_gid()
        if gid:
            if self.state == self.ABSENT:
                self.report.info('Removing')
                shell(['delgroup', self.name])
        else:
            if self.state == self.EXISTS:
                self.report.info('Creating')
                cmd = ['addgroup']
                if self.gid:
                    cmd.extend(['--gid', self.gid])
                cmd.append(self.name)
                shell(cmd)
