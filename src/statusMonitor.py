import enum
import logging
from datetime import datetime


class Status(enum.Enum):
    ACTIVATED = 1
    DEACTIVATED = 0


class StatusMonitor:

    logger = logging.getLogger()

    def __init__(self):
        self.status = Status.DEACTIVATED
        self._set_timestamp()
        self.last_change_by = "startup"

    def set_active(self, active, changed_by="http_request"):
        if active:
            self.status = Status.ACTIVATED
        else:
            self.status = Status.DEACTIVATED
        self._set_timestamp()
        self.last_change_by = changed_by
        self.logger.info("New status: " + str(self.status.name) + ".")

    def _set_timestamp(self):
        self.last_change = datetime.now()
