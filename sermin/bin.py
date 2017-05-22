"""
Shell command

This is installed to the system by the entry_points directive in setup.py

To use without installation, see __main__.py
"""
import sys

from .config import parse_args
from .core import Sermin


def shell_exec():
    args, kwargs = parse_args(sys.argv[1:])
    if not args:
        raise ValueError('You must specify a blueprint')
    elif len(args) > 1:
        raise ValueError('You can only specify one blueprint')

    sermin = Sermin(args[0], **kwargs)
    sermin.run()
