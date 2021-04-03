import enum
import logging
from datetime import datetime
from pubsub import pub


class Status(enum.Enum):
    SCAN_COMPLETE = 4
    SCANNING = 3
    MODIFYING = 2
    ACTIVATED = 1
    DEACTIVATED = 0


class StatusMonitor:

    TOPIC = "status-change"

    logger = logging.getLogger()

    def __init__(self):
        pub.subscribe(self._handle_message, self.TOPIC)
        pub.sendMessage(self.TOPIC, status=Status.DEACTIVATED, changed_by="startup")

    def _handle_message(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        if status == Status.SCAN_COMPLETE:
            self._handle_scan_complete_message(changed_by, scheduled_deactivation)
        else:
            self._handle_standard_message(status, changed_by, scheduled_deactivation)

    def _handle_standard_message(self, status, changed_by, scheduled_deactivation):
        self.status = status
        self.last_change = datetime.now()
        self.last_change_by = changed_by
        self.scheduled_deactivation = scheduled_deactivation
        self.logger.info("New status: " + str(self.status.name) + ".")

    def _handle_scan_complete_message(self, changed_by, scheduled_deactivation):
        if self.status == Status.SCANNING:
            self._handle_standard_message(Status.ACTIVATED, changed_by, scheduled_deactivation)
