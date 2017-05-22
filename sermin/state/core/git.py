"""
Execute command
"""
from collections import defaultdict
from future.utils import python_2_unicode_compatible
import os
import re

from ...utils import shell
from ..base import State
from .dirs import Dir


class Repository(object):
    """
    Class to manage a git repository for the Git state

    An instance will have the following keys:
        branch      String  The name of the current branch
        branches    List    The names of all branches
        tags        List    The names of all tags
        changed     Bool    Whether or not the working directory has
                            uncommitted changes
    """
    path = None

    def __init__(self, path, remote):
        self.path = os.path.normpath(path)
        self.remote = remote

    def __str__(self):
        return self.path

    def git(self, cmd):
        return shell('cd {path} && git {cmd}'.format(path=self.path, cmd=cmd))

    def clone(self):
        """
        Clone the specified repository
        """
        response = shell('cd {parent} && git clone {remote} {dir}'.format(
            parent=os.path.dirname(self.path),
            remote=self.remote,
            dir=os.path.basename(self.path),
        ))
        if 'done.' not in response:
            raise ValueError('Unexpected response from git clone: {}'.format(
                response,
            ))

    def checkout(self, commit=None, tag=None, branch=None):
        """
        Perform `git checkout`
        """
        if tag:
            commit_id = self.tag_commit(tag)
        elif commit:
            commit_id = commit
        elif branch:
            commit_id = branch
        else:
            raise ValueError(
                'Repository checkout requires a commit, tag or branch',
            )

        return shell('cd {path} && git checkout {commit_id}'.format(
            path=self.path,
            commit_id=commit_id,
        ))

    def fetch(self):
        """
        Ensure the repository is using the specified remote as origin and fetch
        """
        self.git('remote set-url origin {remote}'.format(remote=self.remote))
        return self.git('fetch --tags origin'.format(remote=self.remote))

    def pull(self):
        """
        Perform `git pull`
        """
        self.git('pull')

    @property
    def status(self):
        """
        Return a dict of the `git status` data

            branch      str: Current branch
            ahead       bool: True if ahead of the remote
            changed     bool: True if this has changed since the last commit
        """
        # Status command returns false, so has to be followed by true
        raw_status = self.git('status; true')
        m = re.search('# On branch (.+?)\s', raw_status)
        return {
            'branch': m.group(1) if m else '',
            'ahead': ("Your branch is ahead of" in raw_status),
            'changed': ("nothing to commit" in raw_status),
        }

    @property
    def current_commit(self):
        """
        Return the current commit that the repo is on
        """
        return self.git('rev-parse --verify HEAD')

    def branch_head(self, branch):
        """
        Return the current commit of the specified local branch
        """
        return self.git(
            'show-ref --hash --verify refs/heads/{branch}'.format(
                branch=branch
            )
        )

    def origin_branch_head(self, branch):
        """
        Return the current commit of the specified branch on remote origin
        """
        return self.git(
            'show-ref --hash --verify refs/remotes/origin/{branch}'.format(
                branch=branch
            )
        )

    def tag_commit(self, tag):
        """
        Return the commit of the specified tag (dereferenced if it's annotated)
        """
        return self.git('rev-list -1 refs/tags/{tag}'.format(tag=tag))

    @property
    def remotes(self):
        """
        Return dict of remotes as {fetch: .., push:.. } dicts
        """
        raw_remotes = self.git('remote --verbose')
        remotes = defaultdict(dict)
        for raw_remote in raw_remotes.splitlines():
            name, rest = raw_remote.split('\t', 1)
            remote, action = rest.rsplit(' ', 1)
            action = action[1:-1]
            remotes[name][action] = remote
        return remotes

    @property
    def current_branch(self):
        """
        Current branch
        """
        return self.status['branch']

    @property
    def branches(self):
        """
        Return a list of branches from `git branch --list`
        """
        raw_branches = self.git('branch --list')
        branches = [
            branch.lstrip(' *') for branch in raw_branches.splitlines()
        ]
        return branches

    def is_branch(self, object_name):
        return (object_name in self.branches)

    @property
    def tags(self):
        """
        Return a list of tags from `git tag --list`
        """
        raw_tags = self.git('tags --list')
        tags = raw_tags.splitlines()
        return tags

    def is_tag(self, object_name):
        return (object_name in self.tags)

    def __repr__(self):
        return '<Repository {}>'.format(self.path)


@python_2_unicode_compatible
class Git(State):
    default_branch = 'master'

    def __init__(
        self, path, remote=None, commit=None, tag=None, branch=None, **kwargs
    ):
        """
        Arguments
            path        Path to git repository root
            remote      Git remote
            commit      The commit this repository should be on
            tag         The tag this repository should be on
            branch      The branch this repository should be at the HEAD of

        Only specify one of commit, tag or branch.
        If none are specified, defaults to branch=self.default_branch
        """
        if sum(map(bool, [commit, tag, branch])) > 1:
            raise ValueError('A Git can only have one commit, tag or branch')

        if not any([commit, tag, branch]):
            branch = self.default_branch

        self.path = path
        self.remote = remote
        self.commit = commit
        self.tag = tag
        self.branch = branch
        super(Git, self).__init__(**kwargs)

        self.repo = Repository(self.path, self.remote)

        # Add dependency for parent Dir
        self.children.add(
            Dir(os.path.dirname(self.path))
        )

    def check(self):
        # Path exists as a repo?
        if not os.path.exists(self.path):
            self.report.debug('Path does not exist')
            return False

        if (
            not os.path.isdir(self.path) or
            not os.path.isdir(os.path.join(self.path, '.git'))
        ):
            raise ValueError('Git path exists but is not a git repository')

        # Remote origin is this remote?
        remotes = self.repo.remotes
        if (
            'origin' not in remotes or
            remotes['origin']['fetch'] != self.remote
        ):
            self.report.debug('Remote origin does not match')
            return False

        # Repo is at revision/head?
        self.report.info('Fetching remote')
        self.repo.fetch()
        current_commit = self.repo.current_commit
        if (
            self.commit and
            current_commit != self.commit
        ):
            self.report.debug(
                'Commit specified but current commit does not match',
            )
            return False
        if (
            self.tag and
            current_commit != self.repo.tag_commit(self.tag)
        ):
            self.report.debug(
                'Tag specified but current commit does not match',
            )
            return False

        if (
            self.branch and
            current_commit != self.repo.origin_branch_head(self.branch)
        ):
            self.report.debug(
                'Branch specified but current branch does not match',
            )
            return False

        self.report.debug('Repository in expected state')
        return True

    def apply(self):
        # If path does not exist, clone from remote
        if not os.path.isdir(self.path):
            self.report.info('Cloning')
            self.repo.clone()
        # Otherwise self.check() has already `fetch`ed from remote

        # Check out revision/head
        if self.commit:
            self.report.info('Checking out commit {}'.format(self.commit))
        elif self.tag:
            self.report.info('Checking out tag {}'.format(self.tag))
        elif self.branch:
            self.report.info('Checking out branch {}'.format(self.branch))

        self.repo.checkout(
            commit=self.commit,
            tag=self.tag,
            branch=self.branch,
        )
        if self.branch:
            self.report.info('Pulling branch from remote')
            self.repo.pull()
