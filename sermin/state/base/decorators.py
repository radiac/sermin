"""
Decorators for ad-hoc methods
"""
from future.utils import python_2_unicode_compatible

from .state import State

__all__ = ['wrap', 'check', 'apply']


@python_2_unicode_compatible
class AdHocState(State):
    """
    An ad-hoc state is callable, to mimic the original function definition
    """
    def __init__(self, id):
        self.id = id
        super(AdHocState, self).__init__()

    def __str__(self):
        return self.id

    def __call__(self):
        return self.wrapped_fn()


class CheckState(AdHocState):
    """
    An ad-hoc state to return a check status.
    Intended to be used with decorator keywords
    """
    def check(self):
        return self.wrapped_fn()

    def apply(self):
        """Empty state to avoid NotImplementedError"""
        pass


class ApplyState(AdHocState):
    """
    An ad-hoc state to perform an action
    """
    def check(self):
        """Always apply"""
        return False

    def apply(self):
        return self.wrapped_fn()


def wrap(cls, fn, listen, notify):
    def wrapped(fn):
        # Create class with camelified fn title
        cls_name = '{}{}'.format(
            fn.__name__.replace('_', ' ').title().replace(' ', ''),
            cls.__name__,
        )

        new_cls = type(cls_name, (cls,), {})
        new_cls.wrapped_fn = lambda self: fn()

        # Instantiate state
        obj = new_cls('{}-{}'.format(fn.__name__, id(new_cls)))
        if listen:
            obj.listen(listen)
        if notify:
            obj.notify(notify)
        return obj

    if fn:
        return wrapped(fn)
    return wrapped


def check(fn=None, listen=None, notify=None):
    """
    Create a class with this as the check and an empty apply
    """
    return wrap(CheckState, fn, listen, notify)


def apply(fn=None, listen=None, notify=None):
    """
    Create a class with check=True and this as the apply
    """
    return wrap(ApplyState, fn, listen, notify)
