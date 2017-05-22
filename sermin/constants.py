"""
Sermin constants
"""

Undefined = object()


VERBOSITY_DEBUG = 'debug'  # Decisions
VERBOSITY_INFO = 'info'  # Actions
VERBOSITY_WARNING = 'warning'  # Warnings
VERBOSITY_ERROR = 'error'  # Errors
VERBOSITY_LEVEL = {
    verbosity: level for level, verbosity in enumerate([
        VERBOSITY_DEBUG, VERBOSITY_INFO, VERBOSITY_WARNING, VERBOSITY_ERROR,
    ])
}
