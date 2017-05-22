"""
Test the Git state
"""
import os

from sermin import Git
from sermin.utils import shell

from .utils import FullTestCase


class GitTest(FullTestCase):
    # Root path to use for tests
    root_path = '/tmp/sermin_test'
    source = '/tmp/sermin_test/source'
    target = '/tmp/sermin_test/target'

    def setUp(self):
        super(GitTest, self).setUp()
        shell('mkdir -p {}'.format(self.root_path))

    def clean(self):
        shell('rm -rf {}'.format(self.root_path))

    def mk_repo(self, path):
        shell('mkdir {}'.format(path))
        shell('cd {} && git init'.format(path))
        self.mk_commit(path, 'rev1')
        self.mk_commit(path, 'rev2')
        self.mk_commit(path, 'rev3')

    def mk_commit(self, path, rev):
        shell((
            'cd {path} && '
            'touch {rev} &&'
            'git add . && '
            'git commit -m "{rev}"'
        ).format(path=path, rev=rev))

    def get_commits(self, path):
        commits = {}
        for line in shell(
            'cd {} && git log --pretty=oneline'.format(path)
        ).splitlines():
            commit, label = line.split(' ')
            commits[label] = commit
        return commits

    def get_current_commit(self, path):
        return shell('cd {} && git rev-parse --verify HEAD'.format(path))

    def test_mk_repo(self):
        # Check repo is made as expected
        self.mk_repo(self.source)
        commits = self.get_commits(self.source)
        self.assertEqual(len(commits), 3)
        self.assertEqual(
            sorted(commits.keys()),
            ['rev1', 'rev2', 'rev3'],
        )

    def test_clone_repo(self):
        # Clone
        self.mk_repo(self.source)
        Git(self.target, remote=self.source)
        self.registry_run()

        # Check something happened
        self.assertTrue(os.path.isdir(self.target))
        self.assertTrue(os.path.isdir(os.path.join(self.target, '.git')))

        # Check commit history
        source_commits = self.get_commits(self.source)
        target_commits = self.get_commits(self.target)
        self.assertEqual(source_commits, target_commits)

    def test_update_repo(self):
        # Set up initial clone
        self.mk_repo(self.source)
        Git(self.target, remote=self.source)
        self.registry_run()

        # Make change and re-assert state
        self.mk_commit(self.source, 'rev4')
        self.registry.clear()
        Git(self.target, remote=self.source)
        self.registry_run()

        # Compare
        self.assertTrue(os.path.exists(os.path.join(self.target, 'rev4')))
        source_commits = self.get_commits(self.source)
        target_commits = self.get_commits(self.target)
        self.assertEqual(source_commits, target_commits)

    def test_specific_commit(self):
        self.mk_repo(self.source)
        source_commits = self.get_commits(self.source)
        Git(self.target, remote=self.source, commit=source_commits['rev2'])
        self.registry_run()

        # Check repo is on correct commit
        self.assertEqual(
            self.get_current_commit(self.target),
            source_commits['rev2'],
        )

        # Double check by looking at files
        self.assertTrue(os.path.exists(os.path.join(self.target, 'rev2')))
        self.assertFalse(os.path.exists(os.path.join(self.target, 'rev3')))

    def test_specific_tag(self):
        self.mk_repo(self.source)
        source_commits = self.get_commits(self.source)
        shell('cd {path} && git tag -a tag1 {commit} -m "tag 1"'.format(
            path=self.source,
            commit=source_commits['rev2'],
        ))
        Git(self.target, remote=self.source, tag="tag1")
        self.registry_run()

        # Check repo is on correct commit
        self.assertEqual(
            self.get_current_commit(self.target),
            source_commits['rev2'],
        )

        # Double check by looking at files
        self.assertTrue(os.path.exists(os.path.join(self.target, 'rev2')))
        self.assertFalse(os.path.exists(os.path.join(self.target, 'rev3')))

    def test_specific_branch(self):
        # Create a branch and check back to master to ensure it's not a copy
        self.mk_repo(self.source)
        shell('cd {path} && git checkout -b test'.format(path=self.source))
        self.mk_commit(self.source, 'rev4')
        shell('cd {path} && git checkout master'.format(path=self.source))
        Git(self.target, remote=self.source, branch='test')
        self.registry_run()

        # Check repo is on correct commit
        target_commits = self.get_commits(self.target)
        self.assertIn('rev4', target_commits)
        self.assertEqual(
            self.get_current_commit(self.target),
            target_commits['rev4'],
        )

        # Double check by looking at files
        self.assertTrue(os.path.exists(os.path.join(self.target, 'rev4')))
