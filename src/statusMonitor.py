import enum
import logging
from datetime import datetime


class Status(enum.Enum):
    MODIFYING = 2
    ACTIVATED = 1
    DEACTIVATED = 0


class StatusMonitor:

    logger = logging.getLogger()

    def __init__(self):
        self.status = Status.DEACTIVATED
        self._set_timestamp()
        self.last_change_by = "startup"
        self.scheduled_deactivation = None

    def set_status(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.status = status
        self._set_timestamp()
        self.last_change_by = changed_by
        self.scheduled_deactivation = scheduled_deactivation
        self.logger.info("New status: " + str(self.status.name) + ".")

    def _set_timestamp(self):
        self.last_change = datetime.now()
