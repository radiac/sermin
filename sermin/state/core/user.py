"""
User management
"""
from future.utils import python_2_unicode_compatible
import crypt
import pwd

from ...constants import Undefined
from ...utils import shell
from ..base import State


class UserData(object):
    """
    A representation of available data for a system user
    """
    def __init__(self, shell, home, uid, gid, comment):
        self.shell = shell
        self.home = home
        self.uid = uid
        self.gid = gid
        self.comment = comment


@python_2_unicode_compatible
class User(State):
    """
    User state
    """
    # States
    EXISTS = 'exist'
    ABSENT = 'absent'

    default_shell = '/bin/bash'
    default_home = '/home/{username}',

    def __init__(
        self,
        username,
        state=EXISTS,
        password=None,
        shell=Undefined,
        home=Undefined,
        uid=None,
        group=None,
        comment=None,
        **kwargs
    ):
        """
        Define a user state

        Arguments:
            username    System name of user
            state       The desired user state; one of:
                            User.EXISTS
                                The user will be created if it does not exist.
                            User.ABSENT
                                The user will be remove dif it does exist.
                                Any home directory will not be removed.
                                No other arguments can be provided
            password    Optional: password for user, in plain text
            shell       Shell for user. Set to `None` for no shell.
                        Default: User.default_shell
            home        Home path for user.
                        Set to `None` for no home directory.
                        Can contain `format` reference `{username}`.
                        Default: User.default_home
            uid         Optional: numeric user ID to use.
                        Must not already be in use on the system.
                        Values between 0 and 999 are typically reserved for
                        system users.
            group       Optional: primary group for the user.
                        Can either be a gid or a Group state instance.
                        If not set, will allow `useradd` to fall back to its
                        default of creating a group with the same name as the
                        username.
            comment     Optional: text string to describe the login (eg user's
                        full name)
        """
        # TODO: Add extra groups
        super(User, self).__init__(**kwargs)
        self.username = username
        self.state = state
        self.password = password

        if shell is Undefined:
            self.shell = self.default_shell
        else:
            self.shell = shell

        if home is Undefined:
            self.home = self.default_home
        else:
            self.home = home

        self.uid = uid
        self.group = group
        self.comment = comment

    def get_user_status(self):
        """
        Returns a UserData object, or None if the user is not found
        """
        try:
            data = pwd.getpwnam(self.username)
        except KeyError:
            return None
        return UserData(
            shell=data.pw_shell,
            home=data.pw_dir,
            uid=data.pw_uid,
            gid=data.pw_gid,
            comment=data.pw_gecos,
        )

    def check(self):
        user = self.get_user_status()
        if user:
            if self.state == self.EXISTS:
                self.report.debug('Already exists')

                # TODO: Check other attributes match

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
        user = self.get_user_status()
        if user:
            if self.state == self.ABSENT:
                self.report.info('Removing')
                shell('userdel {}'.format(self.username))
        else:
            if self.state == self.EXISTS:
                self.report.info('Creating')
                shell(self.get_add_command())

                # TODO: Check if other attributes need updating

    def get_add_command(self):
        cmd = ['useradd']

        if self.password:
            cmd.extend([
                '-p', crypt.crypt(self.password, crypt.mksalt())
            ])

        if self.shell:
            cmd.extend(['-s', self.shell])

        if self.home:
            cmd.extend([
                '-d',
                self.home.format(username=self.username),
                '-m',  # create it if it doesn't exist
            ])

        if self.uid:
            cmd.extend(['-u', self.uid])

        if self.group:
            cmd.extend(['-g', self.group])

        if self.comment:
            cmd.extend(['-c', self.comment])

        cmd.append(self.username)
        return cmd
