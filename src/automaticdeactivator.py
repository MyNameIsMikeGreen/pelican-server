import logging
from threading import Timer

from statusMonitor import Status


class AutomaticDeactivator:

    DEFAULT_TIMEOUT_SECONDS = 21600

    logger = logging.getLogger()

    def __init__(self, command_executor, status_monitor, timeout_seconds=DEFAULT_TIMEOUT_SECONDS):
        self.command_executor = command_executor
        self.status_monitor = status_monitor
        self.timeout_seconds = timeout_seconds
        self._initialise_timer(timeout_seconds)

    def reset_timer(self, timeout_seconds=None):
        if timeout_seconds:
            self.timeout_seconds = timeout_seconds
        self.timer.cancel()
        self._initialise_timer(self.timeout_seconds)

    def _initialise_timer(self, timeout_seconds):
        self.timer = Timer(timeout_seconds, self._deactivate)
        self.timer.start()
        self.logger.info("Timer initialised.")

    def _deactivate(self):
        self.logger.info("Automatic deactivation triggered.")
        if self.status_monitor.status == Status.DEACTIVATED:
            return
        self.command_executor.deactivate()
        self.status_monitor.set_status(Status.DEACTIVATED, changed_by="automatic_deactivator")
