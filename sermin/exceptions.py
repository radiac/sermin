"""
Sermin exceptions
"""


class RunError(Exception):
    """
    Sermin error during a blueprint run
    """
    pass


class ShellError(RunError):
    """
    Sermin shell command failed
    """
    pass
