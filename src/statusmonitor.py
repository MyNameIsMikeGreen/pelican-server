import enum
import logging
from datetime import datetime
from pubsub import pub


class Status(enum.Enum):
    SCANNING = 3
    MODIFYING = 2
    ACTIVATED = 1
    DEACTIVATED = 0


class StatusMonitor:

    TOPIC = "status-change"

    logger = logging.getLogger()

    def __init__(self):
        pub.subscribe(self._set_status, self.TOPIC)
        pub.sendMessage(self.TOPIC, status=Status.DEACTIVATED, changed_by="startup")

    def _set_status(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.status = status
        self.last_change = datetime.now()
        self.last_change_by = changed_by
        self.scheduled_deactivation = scheduled_deactivation
        self.logger.info("New status: " + str(self.status.name) + ".")
