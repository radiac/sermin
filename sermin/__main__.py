"""
Support use of sermin directory, without entry_points installation:

    python -m sermin <args>
"""

from .bin import shell_exec
shell_exec()
