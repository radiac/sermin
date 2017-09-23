"""
Test the Group state
"""
import unittest

from sermin import User, Group
from sermin.utils import shell, ShellError

from .test_state_group import GroupTestCase, Data


class UserTest(GroupTestCase):
    user_name = 'usertest'
    user_password = 'testpassword'
    user_id = 1010
    user_shell = '/bin/testshell'
    user_home = '/tmp/testuser'
    user_comment = 'Test User'

    def clean(self):
        """
        Ensure group does not exist
        """
        shell('deluser {}'.format(self.user_name), expect_errors=True)
        shell('rm -rf {}'.format(self.user_home), expect_errors=True)
        super(UserTest, self).clean()

    def get_sys_user(self):
        """
        Get line from /etc/passwd

        Format: <user_name>:x:<uid>:<gid>:<comment>:<home>:<shell>
        """
        line = shell(
            'grep "{}:" /etc/passwd'.format(self.user_name),
            expect_errors=True,
        )
        if not line:
            return None
        parts = line.split(':')
        return Data(
            user_name=parts[0],
            user_id=int(parts[2]),
            group_id=int(parts[3]),
            comment=parts[4],
            home=parts[5],
            shell=parts[6],
        )

    def test_adds_without_uid(self):
        user_data = self.get_sys_user()
        self.assertEqual(user_data, None)

        user = User(name=self.user_name)
        self.registry_run()

        # Check the user object can detect its values
        user_status = user.get_user_status()
        self.assertTrue(user_status.uid > 0)

        # Check we can find its values
        user_data = self.get_sys_user()
        self.assertEqual(user_data.user_name, self.user_name)
        self.assertTrue(user_data.user_id > 0)

    def test_adds_with_uid(self):
        user_data = self.get_sys_user()
        self.assertEqual(user_data, None)

        user = User(name=self.user_name, uid=self.user_id)
        self.registry_run()

        user_status = user.get_user_status()
        self.assertEqual(user_status.uid, self.user_id)

        user_data = self.get_sys_user()
        self.assertEqual(user_data.user_name, self.user_name)
        self.assertEqual(user_data.user_id, self.user_id)

    def test_adds_with_password(self):
        user_data = self.get_sys_user()
        self.assertEqual(user_data, None)

        group = Group(name='sudo')
        user = User(
            name=self.user_name,
            password=self.user_password,
            group=group,
        )
        self.registry_run()

        user_status = user.get_user_status()
        self.assertTrue(user_status.uid > 0)

        # Check the user is in the system
        user_data = self.get_sys_user()
        self.assertEqual(user_data.user_name, self.user_name)

        # Check the password itself - we're root, so need to switch to the user
        response = shell(
            'sudo -u {user} sudo -k -l -S'.format(
                user=self.user_name
            ),
            stdin='{password}\n'.format(password=self.user_password),
        )
        self.assertIn('ALL', response)

        # Confirm that the incorrect password fails
        with self.assertRaisesRegexp(
            ShellError,
            r'1 incorrect password attempt',
        ):
            shell(
                'sudo -u {user} sudo -k -l -S'.format(
                    user=self.user_name
                ),
                stdin='x\n',
            )

    def test_adds_with_data(self):
        user_data = self.get_sys_user()
        self.assertEqual(user_data, None)

        group = Group(name=self.group_name, gid=self.group_id)
        user = User(
            name=self.user_name,
            shell=self.user_shell,
            home=self.user_home,
            group=group,
            comment=self.user_comment,
        )
        self.registry_run()

        user_status = user.get_user_status()
        self.assertEqual(user_status.shell, self.user_shell)
        self.assertEqual(user_status.home, self.user_home)
        self.assertTrue(user_status.uid > 0)
        self.assertEqual(user_status.gid, group.get_gid())
        self.assertEqual(user_status.comment, self.user_comment)

        user_data = self.get_sys_user()
        self.assertEqual(user_data.user_name, self.user_name)
        self.assertEqual(user_data.shell, self.user_shell)
        self.assertEqual(user_data.home, self.user_home)
        self.assertEqual(user_data.group_id, group.get_gid())
        self.assertEqual(user_data.comment, self.user_comment)

    @unittest.skip
    def test_removes(self):
        shell('useradd -u {uid} {name}'.format(
            name=self.user_name,
            uid=self.user_id,
        ))
        user_data = self.get_sys_user()
        self.assertEqual(user_data.user_id, self.user_id)

        User(name=self.user_name, state=User.ABSENT)
        self.registry_run()

        user_data = self.get_sys_user()
        self.assertEqual(user_data, None)

    @unittest.skip
    def test_update_data(self):
        pass

    @unittest.skip
    def test_update_password(self):
        pass
