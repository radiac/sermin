"""
Sermin reporting
"""
from .config import settings
from .constants import (
    VERBOSITY_LEVEL,
    VERBOSITY_DEBUG, VERBOSITY_INFO,
    VERBOSITY_WARNING, VERBOSITY_ERROR,
)


class Report(object):
    def __init__(self, label=None):
        self.label = label

    def report(self, level, msg, label=None):
        if level >= VERBOSITY_LEVEL[settings.sermin.verbosity]:
            for line in msg.splitlines():
                print('[{}] {}'.format(label or self.label or '-', line))

    def debug(self, msg, label=None):
        self.report(VERBOSITY_DEBUG, msg, label)

    def info(self, msg, label=None):
        self.report(VERBOSITY_INFO, msg, label)

    def warning(self, msg, label=None):
        self.report(VERBOSITY_WARNING, msg, label)

    def error(self, msg, label=None):
        self.report(VERBOSITY_ERROR, msg, label)


_report = Report()


def debug(msg, label=None):
    _report.debug(msg, label)


def info(msg, label=None):
    _report.info(msg, label)


def warning(msg, label=None):
    _report.warning(msg, label)


def error(msg, label=None):
    _report.error(msg, label)
