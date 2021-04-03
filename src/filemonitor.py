import logging

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

    logger = logging.getLogger()

    def __init__(self):
        super().__init__()

    def on_modified(self, event: FileSystemEvent):
        super().on_modified(event)
        self.logger.info("Log file modified")
        minidlna_is_scanning = self._minidlna_is_scanning(event.src_path)
        if minidlna_is_scanning is None:
            self.logger.info("Unable to determine scan state")
            return
        if minidlna_is_scanning:
            self.logger.info("Minidlna is scanning")
            pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCANNING)
        else:
            self.logger.info("Minidlna is not scanning")
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
            for log_line in reversed(log_file.readlines()):
                if "warn: Scanning" in log_line:
                    if "finished" in log_line:
                        return False
                    else:
                        return True
        return None
