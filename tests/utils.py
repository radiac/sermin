"""
Test utils
"""
from collections import defaultdict
import os

import unittest

from sermin.config import settings
from sermin.state.base.registry import registry


class RegistryTestMixin(object):
    registry = registry

    def setUp(self):
        self.registry.clear()
        self.clean()

    def tearDown(self):
        self.registry.clear()
        self.clean()

    def clean(self):
        pass

    def registry_run(self):
        self.registry.run()


class SafeTestCase(RegistryTestMixin, unittest.TestCase):
    pass


@unittest.skipIf(
    os.environ.get('SERMIN_TEST_MODE', 'safe').lower() == 'full',
    'Not tested in safe mode'
)
class FullTestCase(RegistryTestMixin, unittest.TestCase):
    pass


def with_settings(**values):
    originals = defaultdict(dict)

    def test_outer(fn):
        def test_inner(*args, **kwargs):
            # Override setting
            namespaces = settings._namespaces
            for key, value in values.items():
                namespace, setting = key.split('__')
                originals[namespace][setting] = getattr(
                    namespaces[namespace], setting,
                )
                setattr(namespaces[namespace], setting, value)

            returned = fn(*args, **kwargs)

            # Restore original setting
            for key in values.keys():
                namespace, setting = key.split('__')
                setattr(
                    namespaces[namespace],
                    setting,
                    originals[namespace][setting],
                )

            return returned
        return test_inner
    return test_outer
