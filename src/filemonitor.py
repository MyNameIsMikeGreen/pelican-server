from collections import deque

from pubsub import pub
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer

from statusmonitor import StatusMonitor, Status


class MinidlnaLogMonitor:
    __slots__ = ["path", "observer", "event_handler"]

    def __init__(self, log_path="/var/log/minidlna.log"):
        self.path = log_path
        self.observer = Observer()
        self.event_handler = MinidlnaLogFileEventHandler()
        self.observer.schedule(self.event_handler, self.path)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()


class MinidlnaLogFileEventHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()

    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        is_scanning = self._minidlna_is_scanning(event.src_path)
        if is_scanning is None:
            return
        if is_scanning:
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCANNING)
        elif not is_scanning:
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.NOT_SCANNING)

    @staticmethod
    def _minidlna_is_scanning(log_path):
        """
        Given a miniDLNA log file. Determines whether miniDLNA is currently scanning.
        If the answer cannot be determined, None is returned.
        :param log_path: Path to log file.
        :return: True if scanning. False if not scanning. None if state is unknown.
        """
        with open(log_path) as log_file:
            for log_line in reversed(log_file.readlines()):
                if "warn: Scanning" in log_line and "finished" in log_line:
                    return False
                if "warn: Scanning" in log_line and "finished" not in log_line:
                    return True
        return None
