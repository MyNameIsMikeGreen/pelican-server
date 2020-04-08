import enum
from datetime import datetime


class Status(enum.Enum):
    ACTIVATED = 1
    DEACTIVATED = 0


class StatusMonitor:

    def __init__(self):
        self.status = Status.DEACTIVATED
        self._set_timestamp()

    def set_active(self, active):
        if active:
            self.status = Status.ACTIVATED
        else:
            self.status = Status.DEACTIVATED
        self._set_timestamp()

    def _set_timestamp(self):
        self.last_change = datetime.now()
