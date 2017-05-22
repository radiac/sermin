"""
Packages management
"""
from future.utils import python_2_unicode_compatible

from ...utils import shell, ShellError
from ..base import State


@python_2_unicode_compatible
class Package(State):
    apt_updated = False

    # States
    INSTALLED = 'installed'
    ABSENT = 'absent'

    def __init__(self, name, state=INSTALLED, **kwargs):
        """
        Define the package state

        Arguments:
            name        The name of the package
            state       The desired package state; one of:
                            Package.INSTALLED
                                Install if missing
                            Package.ABSENT
                                Remove if present
        """
        if state not in [self.INSTALLED, self.ABSENT]:
            raise ValueError('Unexpected state {}'.format(state))
        self.name = name
        self.state = state
        self.want_installed = (self.state == self.INSTALLED)
        super(Package, self).__init__(**kwargs)

    def __str__(self):
        return self.name

    def check(self):
        # Find it it's installed
        output = shell('dpkg -s {}'.format(self.name), expect_errors=True)
        if 'Status: install ok installed' in output:
            self.is_installed = True
        elif "package '{}' is not installed".format(self.name) in output:
            self.is_installed = False
        else:
            raise ShellError('Unexpected dpkg output:\n{}'.format(output))

        # Determine state
        if self.is_installed == self.want_installed:
            # Either is installed and want installed,
            # or not installed and don't want installed.
            # State matches what we want, check passes
            if self.is_installed:
                self.report.debug('Already installed')
            else:
                self.report.debug('Already not installed')
            return True

        if self.is_installed:
            self.report.debug('Installed but should not be')
        else:
            self.report.debug('Not installed but should be')
        return False

    def apply(self):
        # Make sure apt is updated
        self.update_apt()

        if self.is_installed and not self.want_installed:
            # Installed but not wanted
            self.report.info('Removing')
            self.remove()

        elif not self.is_installed and self.want_installed:
            # Not installed but wanted
            self.report.info('Installing')
            self.install()

    def update_apt(self):
        """
        Update apt once, regardless of how many Package instances there are
        """
        if self.__class__.apt_updated:
            return
        shell('apt-get update')
        self.__class__.apt_updated = True

    def install(self):
        shell('apt-get install --yes {}'.format(self.name))
        self.is_installed = True

    def remove(self):
        shell('apt-get remove --purge --yes {}'.format(self.name))
        self.is_installed = False
