"""
Service management
"""
from future.utils import python_2_unicode_compatible
import psutil

from ...utils import shell
from ..base import State


@python_2_unicode_compatible
class Service(State):
    # States
    RUNNING = 'running'
    STOPPED = 'stopped'

    # Actions
    RESTART = 'restart'
    RELOAD = 'reload'
    FORCE_RELOAD = 'force-reload'

    def __init__(
        self, name, state=RUNNING, action=None,
        command='/etc/init.d/{name} {action}',
        **kwargs
    ):
        """
        Define the service state

        Arguments:
            name        The name of the package
            state       The desired package state; one of:
                            Service.RUNNING
                                Start if not running
                            Service.STOPPED
                                Stop if running
            action      Action to perform if state is RUNNING. Can be any
                        string value accepted by the service definition, or one
                        of:
                            Service.RESTART         restart
                            Service.RELOAD          reload
                            Service.FORCE_RELOAD    force-reload
            command     The shell command to apply the state to the service
        """
        if state not in (self.RUNNING, self.STOPPED):
            raise ValueError('Invalid state')

        if state == self.STOPPED and action:
            raise ValueError(
                'A State defined in state STOPPED cannot have an action'
            )

        self.name = name
        self.state = state
        self.action = action
        self.command = command
        super(Service, self).__init__(**kwargs)

    def __str__(self):
        return self.name

    def check(self):
        processes = {
            proc.name(): proc for proc in psutil.process_iter()
        }
        self.process = processes.get(self.name)
        self.running = False
        if self.process:
            self.running = True

        if self.state == self.RUNNING:
            if self.running and not self.action:
                self.report.debug('Already running')
                return True
            self.report.debug('Not running but should be')
            return False

        elif self.state == self.STOPPED:
            if self.running:
                self.report.debug('Running but should not be')
                return False
            self.report.debug('Already not running')
            return True

    def apply(self):
        if self.running:
            if self.state == self.STOPPED:
                self.report.info('Stopping')
                shell(self.command.format(name=self.name, action='stop'))
        else:
            if self.state == self.RUNNING:
                self.report.info('Starting')
                shell(self.command.format(name=self.name, action='start'))

        if self.action:
            self.report.info('Performing action: {}'.format(self.action))
            shell(self.command.format(name=self.name, action=self.action))
