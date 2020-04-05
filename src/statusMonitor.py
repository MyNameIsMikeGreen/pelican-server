import enum


class Status(enum.Enum):
    ACTIVE = 1
    DEACTIVE = 0


class StatusMonitor:

    def __init__(self):
        self.status = Status.DEACTIVE

    def set_active(self, active):
        if active:
            self.status = Status.ACTIVE
        else:
            self.status = Status.DEACTIVE
