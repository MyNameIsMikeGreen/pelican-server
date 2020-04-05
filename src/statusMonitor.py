import enum
from datetime import datetime


class Status(enum.Enum):
    ACTIVE = 1
    DEACTIVE = 0


class StatusMonitor:

    def __init__(self):
        self.status = Status.DEACTIVE
        self._set_timestamp()

    def set_active(self, active):
        if active:
            self.status = Status.ACTIVE
        else:
            self.status = Status.DEACTIVE
        self._set_timestamp()

    def _set_timestamp(self):
        self.last_change = datetime.now()
