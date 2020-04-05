import enum


class Status(enum.Enum):
    ACTIVE = 1
    DEACTIVE = 0


class StatusMonitor:

    status = Status.ACTIVE

    def set_active(self, active):
        if active:
            self.status = Status.ACTIVE
        else:
            self.status = Status.DEACTIVE
