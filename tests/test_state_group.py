"""
Test the Group state
"""
import unittest

from sermin import Group
from sermin.utils import shell

from .utils import FullTestCase, Data


class GroupTestCase(FullTestCase):
    group_name = 'grouptest'
    group_id = 1010

    def clean(self):
        """
        Ensure group does not exist
        """
        shell('delgroup {}'.format(self.group_name), expect_errors=True)

    def get_sys_group(self):
        """
        Get line from /etc/group

        Format: <group_name>:x:<group_id>:<members_csv>
        """
        line = shell(
            'grep "{}:" /etc/group'.format(self.group_name),
            expect_errors=True,
        )
        if not line:
            return None
        parts = line.split(':')
        return Data(
            group_name=parts[0],
            group_id=int(parts[2]),
            members=parts[3].split(','),
        )


class GroupTest(GroupTestCase):
    def test_adds_without_gid(self):
        group_data = self.get_sys_group()
        self.assertEqual(group_data, None)

        grp = Group(name=self.group_name)
        self.registry_run()
        self.assertTrue(int(grp.get_gid()) > 0)

        group_data = self.get_sys_group()
        self.assertEqual(group_data.group_name, self.group_name)
        self.assertTrue(group_data.group_id > 0)

    def test_adds_with_gid(self):
        group_data = self.get_sys_group()
        self.assertEqual(group_data, None)

        grp = Group(name=self.group_name, gid=self.group_id)
        self.registry_run()
        self.assertEqual(grp.get_gid(), self.group_id)

        group_data = self.get_sys_group()
        self.assertEqual(group_data.group_id, self.group_id)

    @unittest.skip
    def test_add_group_already_exists(self):
        # TODO: Test that if the group already exists, no change is made
        pass

    @unittest.skip
    def test_add_gid_already_taken(self):
        # TODO: Test that an error is raised if the gid is already taken by
        # another group
        pass

    def test_removes(self):
        shell('addgroup --gid {} {}'.format(self.group_id, self.group_name))
        group_data = self.get_sys_group()
        self.assertEqual(group_data.group_id, self.group_id)

        Group(name=self.group_name, state=Group.ABSENT)
        self.registry_run()
        group_data = self.get_sys_group()
        self.assertEqual(group_data, None)

    @unittest.skip
    def test_group_not_empty_not_removed(self):
        # TODO: Test that a non-empty group fails in the check()
        pass
