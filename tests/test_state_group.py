"""
Test the Group state
"""
import unittest

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

    def get_group_line(self):
        return = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )

    def test_adds_without_gid(self):
        group_line = self.get_group_line()
        self.assertEqual(group_line, '')

        grp = Group(name=self.group_name)
        self.registry_run()
        self.assertTrue(int(grp.get_gid()) > 0)
        group_line = self.get_group_line()
        self.assertRegexpMatches(
            group_line,
            r'^{}:x:\d+:$'.format(self.group_name),
        )

    def test_adds_with_gid(self):
        group_line = self.get_group_line()
        self.assertEqual(group_line, '')

        grp = Group(name=self.group_name, gid=self.group_id)
        self.registry_run()
        self.assertEqual(grp.get_gid(), self.group_id)
        group_line = self.get_group_line()
        self.assertTrue(group_line.endswith('{}:'.format(self.group_id)))

    def test_removes(self):
        shell('addgroup --gid {} {}'.format(self.group_id, self.group_name))
        group_line = self.get_group_line()
        self.assertTrue(group_line.endswith('{}:'.format(self.group_id)))

        Group(name=self.group_name, state=Group.ABSENT)
        self.registry_run()
        group_line = self.get_group_line()
        self.assertEqual(group_line, '')

    @unittest.skip
    def test_group_not_empty_not_removed(self):
        # TODO: Test that a non-empty group fails in the check()
        pass