"""
Test the Command state
"""
import os

from sermin import Command
from sermin.utils import shell

from .utils import FullTestCase


class CommandTest(FullTestCase):
    # Path to use for mkdir tests
    path = '/tmp/sermin_test'

    def clean(self):
        """
        Ensure dir is not on the system
        """
        shell('rm -rf {}'.format(self.path))

    def test_command_runs(self):
        Command('mkdir {}'.format(self.path))
        self.registry_run()
        self.assertTrue(os.path.isdir(self.path))

    def test_command_cwd(self):
        shell('mkdir {}'.format(self.path))
        Command('mkdir test', cwd=self.path)
        self.registry_run()
        self.assertTrue(os.path.isdir(os.path.join(self.path, 'test')))
