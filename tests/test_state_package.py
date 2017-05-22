"""
Test the Package state
"""
from sermin import Package
from sermin.utils import shell

from .utils import FullTestCase


class PackageTest(FullTestCase):
    # Package to use for tests
    package = 'sl'

    def clean(self):
        """
        Ensure package is not on the system
        """
        shell('apt-get remove --purge --yes {}'.format(self.package))

    def test_installs(self):
        Package(self.package)
        self.registry_run()
        output = shell('dpkg -s {}'.format(self.package), expect_errors=True)
        self.assertIn('Status: install ok installed', output)

    def test_uninstalls(self):
        shell('apt-get install --yes {}'.format(self.package))
        Package(self.package, state=Package.ABSENT)
        self.registry_run()
        output = shell('dpkg -s {}'.format(self.package), expect_errors=True)
        self.assertIn(
            "package '{}' is not installed".format(self.package),
            output
        )
