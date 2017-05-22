"""
State registry and base State class
"""
from __future__ import unicode_literals
from builtins import input

from ...config import settings
from ...report import Report
from .registry import registry, StateRegistry


__all__ = ['State']


class StateError(Exception):
    pass


class StateType(type):
    """
    State metaclass

    Registers new State classes with registry
    """
    def __init__(self, name, bases, dct):
        """
        Register state class with registry
        """
        super(StateType, self).__init__(name, bases, dct)
        # Don't register abstract state classes
        if 'abstract' in dct and dct['abstract']:
            return

        # Register
        if not getattr(self, 'registry', None):
            self.registry = registry

        # Move class children to their own registry
        self._class_children = StateRegistry()
        for attr in dct.values():
            if isinstance(attr, State):
                self._class_children.add(attr)


class State(object):
    """
    Base class for state objects

    A state has 3 phases:

    * *init* - where the modules are loaded and desired states defined
    * *check* - where the states are checked against the system
    * *apply* - where the states are applied to the system
    """
    __metaclass__ = StateType
    abstract = True

    # Counter allows the State metaclass to detect the order of child states
    # Class attribute is the value for the next State instance. The __init__
    # method assigns the current value to the instance attribute, then
    # increments the class attribute
    creation_counter = 1

    # Registry this state is registered with
    #
    # When defined as a class attribute, sets the registry that this state
    # should register itself with. If not defined, it will register itself with
    # the default registry.
    #
    # When accessed on an instance, it refers to the registry that the instance
    # is currently registered with. This may not match the class attribute.
    registry = None

    # _is indicates this State's current state - it is the value of the last
    # check() call, either True or False. None means it has not been checked.
    _is = None

    # Listeners for when this state instance changes from False to True
    listeners = None

    # Registry of child states to be checked and applied before this state
    children = None

    # Registry of child states on class - merged with `children` on `__init__`
    _class_children = None

    # Cached Report instance
    _report = None

    # Confirmation message. Subclasses should override this
    @property
    def msg_can_apply_confirm(self):
        return "Apply {} config for {}?".format(
            self.__class__.__name__, self,
        )

    def __init__(self):
        # Increment creation counter so we can maintain order
        self.creation_counter = State.creation_counter
        State.creation_counter += 1

        # Add to this class's chosen registry
        # Need to set it to None before registering
        registry = self.registry
        self.registry = None
        registry.add(self)

        self.listeners = []
        self.children = StateRegistry()
        self.children.extend(self._class_children)

    @property
    def report(self):
        if not self._report:
            self._report = Report('{}: {}'.format(type(self).__name__, self))
        return self._report

    def run_check(self, force=False):
        """
        Check and update the state using check_children and check

        Returns True if state is met and does not need to be applied
        Returns False if state is not met and action needs to be taken
        Raises StateError if there is a problem

        The method performs the checks then updates the internal state.

        If the check has already been run, it will not be run again unless
        `force=True`.

        Subclasses should override the `check` method.

        Child states are checked first.
        """
        if self._is is not None and not force:
            return self._is

        self._is = all([
            self.children.check(),
            self.check(),
        ])
        return self._is

    def check(self):
        """
        Check if the system state matches this class's definition

        Return True if the state is met, False if it is not

        Do not call directly - call run_check() instead

        Subclasses should implement this method
        """
        return True

    def run_apply(self):
        """
        Check the state, and if it is not met, apply the changes.

        If method completes, changes were applied and state is now True.
        Raises StateError if there is a problem

        The base class checks and applies child state instances. Subclasses
        which implement this method should normally perform their actions after
        super.

        Child states are applied first.
        """
        # Check state, skip if ok
        if self._is is None:
            self._is = self.check()

        # If we're already OK, complete
        if self._is:
            self.trigger_completed()
            return

        # See if we can apply
        can = self.can_apply()

        # If we can, apply changes
        if can:
            self.children.apply()
            self.apply()

        # Stage has changed
        self._is = True

        # Trigger any listeners
        self.trigger_changed()
        self.trigger_completed()

    def can_apply(self):
        """
        Can perform the action

        Return True if the apply action can be performed
        Return False if the action cannot, but the process should continue
        Raise StateError if the action cannot, and the process should terminate
        """
        if settings.sermin.dryrun:
            return False

        if not settings.sermin.confirm:
            return True

        answer = input("{} (Y/n)".format(self.msg_can_apply_confirm)).lower()
        if not answer or answer.startswith('y'):
            return True
        else:
            raise StateError("Action cancelled")

    def apply(self):
        """
        Apply this class's state to the system

        Do not call directly - call run_apply() instead
        """
        raise NotImplementedError('Subclasses must implement apply')

    def listen(self, source):
        """
        Tell this instance to listen for a source State's state change
        """
        if not isinstance(source, State):
            raise ValueError('Cannot listen to a non-state source')
        source.listeners.append(self)

    def notify(self, target):
        """
        Tell this instance to notify a target State when this state changes
        """
        if not isinstance(target, State):
            raise ValueError('Cannot notify a non-state target')
        self.listeners.append(target)

    def trigger_changed(self):
        """
        Alert listeners to this State that the state has changed
        """
        for listener in self.listeners:
            listener.handle_changed(self)

    def trigger_completed(self):
        """
        Alert listeners to this State that the state is complete
        """
        for listener in self.listeners:
            listener.handle_completed(self)

    def handle_changed(self, source):
        """
        Called when a state this instance is listening to changes

        Actions taken by this method should be idempotent
        """
        pass

    def handle_completed(self, source):
        """
        Called when a state this instance is listening to finishes

        Actions taken by this method should be idempotent
        """
        pass


class FinalListenerState(State):
    """
    State which keeps track of how many listeners have completed, and will
    call handle_final once the last listener is complete
    """
    def __init__(self, *args, **kwargs):
        super(FinalListenerState, self).__init__(*args, **kwargs)
        self._changed_listeners = []
        self._completed_listeners = 0

    def handle_changed(self, source):
        super(FinalListenerState, self).handle_change(source)
        self._changed_listeners.append(source)

    def handle_completed(self, source):
        self._completed_listeners += 1
        if self._completed_listeners == len(self.listeners):
            self.handle_final()

    def handle_final(self):
        """
        Method called once all the States this State is listening to have
        completed (either after check==True or after apply)
        """
        pass
