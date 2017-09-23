"""
User management
"""
from future.utils import python_2_unicode_compatible
import crypt
import pwd
import random

from ...constants import Undefined
from ...utils import shell
from ..base import State
from .group import Group


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
    default_home = '/home/{name}'

    def __init__(
        self,
        name,
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
            name        System name of user
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
                        Can contain `format` reference `{name}`.
                        Default: User.default_home
            uid         Optional: numeric user ID to use.
                        Must not already be in use on the system.
                        Values between 0 and 999 are typically reserved for
                        system users.
            group       Optional: primary group for the user.
                        Can either be a gid or a Group state instance.
                        If not set, will allow `useradd` to fall back to its
                        default of creating a group with the same name as the
                        username User.name.
            comment     Optional: text string to describe the login (eg user's
                        full name)
        """
        # TODO: Add extra groups
        super(User, self).__init__(**kwargs)
        self.name = name
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
            data = pwd.getpwnam(self.name)
        except KeyError:
            return None
        return UserData(
            shell=data.pw_shell,
            home=data.pw_dir,
            uid=int(data.pw_uid),
            gid=int(data.pw_gid),
            comment=data.pw_gecos,
        )

    def __str__(self):
        uid = self.uid
        if not uid:
            status = self.get_user_status()
            if status:
                uid = status.uid
            else:
                uid = '-'

        return '{name} ({uid})'.format(name=self.name, uid=uid)

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
                shell('userdel {}'.format(self.name))
        else:
            if self.state == self.EXISTS:
                self.report.info('Creating')
                shell(self.get_add_command())

                # TODO: Check if other attributes need updating (usermod)

    def get_add_command(self):
        cmd = ['useradd']

        if self.password:
            ALPHABET = ''.join([
                chr(c) for c in range(48, 58) + range(65, 91) + range(97, 123)
            ])
            salt = ''.join(random.choice(ALPHABET) for i in range(16))
            cmd.extend([
                '-p', crypt.crypt(self.password, salt)
            ])

        if self.shell:
            cmd.extend(['-s', self.shell])

        if self.home:
            cmd.extend([
                '-d',
                self.home.format(name=self.name),
                '-m',  # create it if it doesn't exist
            ])

        if self.uid:
            cmd.extend(['-u', self.uid])

        if self.group:
            if isinstance(self.group, Group):
                gid = self.group.get_gid()
                if not gid:
                    raise ValueError(
                        "Cannot add a user to a group which doesn't exist"
                    )
            else:
                gid = self.group
            cmd.extend(['-g', gid])

        if self.comment:
            cmd.extend(['-c', self.comment])

        cmd.append(self.name)
        return cmd
