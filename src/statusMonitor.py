import enum


class Status(enum.Enum):
    ACTIVE = enum.auto()
    DEACTIVE = enum.auto()


class StatusMonitor:

    status = Status.ACTIVE

    def set_active(self, active):
        if active:
            self.status = Status.ACTIVE
        else:
            self.status = Status.DEACTIVE
