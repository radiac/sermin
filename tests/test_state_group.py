"""
Test the Group state
"""
from sermin import Group
from sermin.utils import shell

from .utils import FullTestCase


class GroupTest(FullTestCase):
    group_name = 'grouptest'
    group_id = '1010'

    def clean(self):
        """
        Ensure group does not exist
        """
        shell('delgroup {}'.format(self.group_name), expect_errors=True)

    def test_adds(self):
        group_line = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )
        self.assertEqual(group_line, '')

        grp = Group(name=self.group_name, gid=self.group_id)
        self.registry_run()
        self.assertEqual(grp.get_gid(), self.group_id)
        group_line = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )
        self.assertTrue(group_line.endswith('{}:'.format(self.group_id)))

    def test_removes(self):
        shell('addgroup --gid {} {}'.format(self.group_id, self.group_name))
        group_line = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )
        self.assertTrue(group_line.endswith('{}:'.format(self.group_id)))

        Group(name=self.group_name, state=Group.ABSENT)
        self.registry_run()
        group_line = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )
        self.assertEqual(group_line, '')
