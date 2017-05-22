"""
Test Sermin state module
"""
import sermin
from sermin import state
from sermin.state.base.registry import registry

from .utils import SafeTestCase, with_settings


class StateTest(SafeTestCase):
    def test_class_does_not_register(self):
        self.assertFalse('MockState' in registry.states)

        class MockState(state.State):
            pass

        self.assertEqual(len(registry.states), 0)

    def test_instance_registers(self):
        class MockState(state.State):
            pass

        mocked = MockState()
        self.assertEqual(len(registry.states), 1)
        self.assertIn(mocked, registry.states)

    @with_settings(sermin__dryrun=True)
    def test_instance_dryrun_checks(self):
        """
        In dry run, only the check runs
        """
        class MockState(state.State):
            applied = False
            checked = False

            def check(self):
                self.checked = True
                return False

            def apply(self):
                self.applied = True

        mocked = MockState()
        registry.run()
        self.assertEqual(mocked.checked, True)
        self.assertEqual(mocked.applied, False)

    @with_settings(sermin__dryrun=False)
    def test_instance_check_passes__not_applied(self):
        """
        Out of dry run, both check and apply run
        """
        class MockState(state.State):
            applied = False
            checked = False

            def check(self):
                self.checked = True
                return True

            def apply(self):
                self.applied = True

        mocked = MockState()
        registry.run()
        self.assertEqual(mocked.checked, True)
        self.assertEqual(mocked.applied, False)

    @with_settings(sermin__dryrun=False)
    def test_instance_check_fails__applied(self):
        """
        Out of dry run, both check and apply run
        """
        class MockState(state.State):
            applied = False
            checked = False

            def check(self):
                self.checked = True
                return False

            def apply(self):
                self.applied = True

        mocked = MockState()
        registry.run()
        self.assertEqual(mocked.checked, True)
        self.assertEqual(mocked.applied, True)


class AdHocStateTest(SafeTestCase):
    def test_check_registers(self):
        self.assertFalse('MockCheckState' in registry.states)

        @sermin.check
        def mock():
            pass

        self.assertEqual(len(registry.states), 1)
        self.assertEqual(
            registry.states[0].__class__.__name__,
            'MockCheckState',
        )

    def test_apply_registers(self):
        self.assertFalse('MockApplyState' in registry.states)

        @sermin.apply
        def mock():
            pass

        self.assertEqual(len(registry.states), 1)
        self.assertEqual(
            registry.states[0].__class__.__name__,
            'MockApplyState',
        )

    def test_check_runs(self):
        mock_run = []

        @sermin.check
        def mock():
            mock_run.append(True)

        registry.run()
        self.assertEqual(len(mock_run), 1)

    def test_apply_runs(self):
        mock_run = []

        @sermin.check
        def mock():
            mock_run.append(True)

        registry.run()
        self.assertEqual(len(mock_run), 1)


class StateNotificationTest(SafeTestCase):
    def test_listen_changed(self):
        """
        The listen() method sets a state to listen to another
        """
        class SourceState(state.State):
            def check(self):
                return False

            def apply(self):
                return

        class ListenerState(state.State):
            heard = None

            def handle_changed(self, source):
                self.heard = source

            def apply(self):
                return

        test_source = SourceState()
        test_listener = ListenerState()
        test_listener.listen(test_source)
        registry.run()

        self.assertEqual(test_listener.heard, test_source)

    def test_notify_changed(self):
        """
        The notify() method sets a state to notify another (reverse listen)
        """
        class SourceState(state.State):
            def check(self):
                return False

            def apply(self):
                return

        class ListenerState(state.State):
            heard = None

            def handle_changed(self, source):
                self.heard = source

            def apply(self):
                return

        test_source = SourceState()
        test_listener = ListenerState()
        test_source.notify(test_listener)
        registry.run()

        self.assertEqual(test_listener.heard, test_source)

    def test_listen__check_passes__completed_triggered(self):
        class SourceState(state.State):
            def check(self):
                return True

            def apply(self):
                return

        class ListenerState(state.State):
            heard = None

            def handle_completed(self, source):
                self.heard = source

            def apply(self):
                return

        test_source = SourceState()
        test_listener = ListenerState()
        test_listener.listen(test_source)
        registry.run()

        self.assertEqual(test_listener.heard, test_source)

    def test_listen__check_fail__completed_triggered(self):
        class SourceState(state.State):
            def check(self):
                return False

            def apply(self):
                return

        class ListenerState(state.State):
            heard = None

            def handle_completed(self, source):
                self.heard = source

            def apply(self):
                return

        test_source = SourceState()
        test_listener = ListenerState()
        test_listener.listen(test_source)
        registry.run()

        self.assertEqual(test_listener.heard, test_source)


class ChildTest(SafeTestCase):
    def test_child_states__not_in_registry_root(self):
        class ChildState(state.State):
            pass

        class ParentState(state.State):
            child = ChildState()

        parent = ParentState()
        self.assertEqual(len(registry.states), 1)
        self.assertEqual(len(parent.children), 1)

    @with_settings(sermin__dryrun=True)
    def test_child_states__check_once(self):
        class ChildState(state.State):
            counter = 0

            def check(self):
                self.counter += 1
                return True

        class ParentState(state.State):
            child = ChildState()
            counter = 0

            def check(self):
                self.counter += 1
                return True

        parent = ParentState()
        registry.run()
        self.assertEqual(parent.counter, 1)
        self.assertEqual(parent.child.counter, 1)

    def test_child_states__apply_once(self):
        class ChildState(state.State):
            check_counter = 0
            apply_counter = 0

            def check(self):
                self.check_counter += 1
                return False

            def apply(self):
                self.apply_counter += 1
                return False

        class ParentState(state.State):
            child = ChildState()

            check_counter = 0
            apply_counter = 0

            def check(self):
                self.check_counter += 1
                return False

            def apply(self):
                self.apply_counter += 1
                return False

        parent = ParentState()
        registry.run()
        self.assertEqual(parent.check_counter, 1)
        self.assertEqual(parent.apply_counter, 1)
        self.assertEqual(parent.child.check_counter, 1)
        self.assertEqual(parent.child.apply_counter, 1)
