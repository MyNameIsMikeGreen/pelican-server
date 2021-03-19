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
        if self._minidlna_is_scanning(event.src_path):
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCANNING)
        else:
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.NOT_SCANNING)

    @staticmethod
    def _minidlna_is_scanning(log_path):
        # [2021/03/15 18:57:03] scanner.c:730: warn: Scanning /mypath
        # [2021/03/15 19:02:09] scanner.c:819: warn: Scanning /mypath finished (2 files)!
        # TODO: Better solution

        with open(log_path) as log_file:
            log_lines = deque(log_file, maxlen=3)
        for log_line in log_lines:
            if "warn: Scanning" in log_line and "finished" not in log_line:
                return True
        return False
