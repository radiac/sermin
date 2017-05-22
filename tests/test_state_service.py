"""
Test the Service state
"""
from sermin import Service
from sermin.utils import shell, ShellError

from .utils import FullTestCase


class ServiceTest(FullTestCase):
    # Service to use for tests
    service = 'atd'

    def clean(self):
        """
        Ensure service is not running
        """
        shell('/etc/init.d/{} stop'.format(self.service))

    def assertRunning(self):
        try:
            pid = shell('pgrep {}'.format(self.service))
        except ShellError:
            self.fail('{} is not running'.format(self.service))
        self.assertRegexpMatches(pid, r'^\d+$')
        return pid

    def assertStopped(self):
        pid = shell('pgrep {}'.format(self.service), expect_errors=True)
        self.assertEqual(pid, '')

    def test_starts(self):
        Service(self.service)
        self.registry_run()
        self.assertRunning()

    def test_restarts(self):
        shell('/etc/init.d/{} start'.format(self.service))
        pid_before = self.assertRunning()

        Service(self.service, action=Service.RESTART)
        self.registry_run()

        pid_after = self.assertRunning()
        self.assertNotEqual(pid_before, pid_after)

    def test_stops(self):
        shell('/etc/init.d/{} start'.format(self.service))
        self.assertRunning()

        Service(self.service, state=Service.STOPPED)
        self.registry_run()
        self.assertStopped()
