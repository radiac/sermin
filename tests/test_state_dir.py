"""
Test the Dir state
"""
import os

from sermin import Dir
from sermin.utils import shell

from .utils import FullTestCase


class DirTest(FullTestCase):
    # Root path to use for tests
    path = '/tmp/sermin_test'

    def setUp(self):
        super(DirTest, self).setUp()
        shell('mkdir -p {}'.format(self.path))

    def clean(self):
        shell('rm -rf {}'.format(self.path))

    def test_create_single_dir(self):
        path = os.path.join(self.path, 'test')
        Dir(path)
        self.registry_run()

    def test_create_parent_path(self):
        path = os.path.join(self.path, 'test', 'deep', 'path')
        Dir(path)
        self.registry_run()
        self.assertTrue(os.path.isdir(path))

    def test_create_remove_dir(self):
        path = os.path.join(self.path, 'test')
        shell('mkdir {}'.format(path))
        Dir(path, state=Dir.ABSENT)
        self.registry_run()
        self.assertFalse(os.path.exists(path))
