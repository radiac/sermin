"""
State registry
"""
from __future__ import unicode_literals
import itertools


__all__ = []


class StateError(Exception):
    pass


class StateRegistry(object):
    """
    State multiton registry
    """
    '''
    Implementation notes

    Problem that needs to be solved: we have multiple lists of objects which
    need to be repeatedly merged and sorted by an attribute.

    Option 1: maintain unsorted lists, then combine and sort when needed
    Option 2: maintain sorted lists, then combine and re-sort when needed
    Option 3: maintain sorted lists, then merge them when they're needed

    Benchmarks were performed for 3 lists of 10,000 items 10,000 times

    Options 2 is slightly faster than option 1, but only by 0.1s; this will be
    lost through the overhead of having to maintain an ordered list (either
    manually or using tuples with bisect.insort and zip to de-tuple). Although
    Option 3 sounds like it should be faster, it was 1m slower.

    If this class needs optimising, the best approach may be to add a listener
    pattern to `extends`, so that `add` can notify interested registries of
    changes, so they can re-generate their ordered state list.
    '''
    _states = None

    def __init__(self):
        self.clear()

    def clear(self):
        if self._states:
            for state in self._states:
                state.registry = None
        self._states = []
        self.registries = []

    def add(self, state):
        """
        Add the state to this registry, and remove it from its current registry
        """
        if state.registry:
            state.registry.remove(state)
        self._states.append(state)
        self._states.sort()
        state.registry = self

    def remove(self, state):
        """
        Remove the state from this registry
        """
        if state.registry != self:
            raise ValueError('Cannot remove this state - not in this registry')
        self._states.remove(state)
        state.registry = None

    def extend(self, registry):
        self.registries.append(registry)

    @property
    def states(self):
        """
        Return a full list of states, in definition order
        """
        return sorted(
            itertools.chain(
                self._states,
                *[registry.states for registry in self.registries]
            ),
            key=lambda obj: obj.creation_counter,
        )

    def __len__(self):
        return len(self.states)

    def check(self):
        """
        Check registry states

        Return False if any state fails
        """
        return all([state.run_check() for state in self.states])

    def apply(self):
        """
        Apply registry states
        """
        for state in self.states:
            state.run_apply()

    def run(self):
        """
        Check all states then apply all states.

        Although each individual `apply` will perform its `check` before making
        changes, this gives late states the opportunity to throw errors during
        their checks, to block earlier states from making any changes.
        """
        self.check()
        self.apply()


registry = StateRegistry()
