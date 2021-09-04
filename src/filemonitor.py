from pubsub import pub
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from statusmonitor import StatusMonitor, Status


class MinidlnaLogMonitor:
    __slots__ = ["path", "observer", "event_handler"]

    def __init__(self, log_path="/var/log/minidlna/minidlna.log"):
        self.path = log_path
        self.observer = Observer()
        self.event_handler = MinidlnaLogFileEventHandler(self.path)
        self.observer.schedule(self.event_handler, self.path)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class MinidlnaLogFileEventHandler(FileSystemEventHandler):

    def __init__(self, log_path):
        super().__init__()
        self.path = log_path

    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        minidlna_is_scanning = self._minidlna_is_scanning(self.path)
        if minidlna_is_scanning is None:
            return
        if minidlna_is_scanning:
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCANNING)
        else:
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCAN_COMPLETE, changed_by="scan_completion")

    @staticmethod
    def _minidlna_is_scanning(log_path):
        """
        Given a miniDLNA log file. Determines whether miniDLNA is currently scanning.
        If the answer cannot be determined, None is returned.
        :param log_path: Path to log file.
        :return: True if scanning. False if not scanning. None if state is unknown.
        """
        with open(log_path) as log_file:
            last_line = log_file.readlines()[-1]
        if "warn: Scanning" in last_line:
            if "finished" in last_line:
                return False
            else:
                return True
