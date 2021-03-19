import os
import sys
import unittest

from busypie import wait, SECOND

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))

from filemonitor import MinidlnaLogMonitor
from statusmonitor import StatusMonitor, Status

TEST_FILE = os.path.dirname(__file__) + "/../testresources/testfile"


class TestITScanning(unittest.TestCase):

    def test_monitor_fires_event_if_scan_state_change_detected(self):
        # Given: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # And: the status monitor is started
        self.status_monitor = StatusMonitor()
        self.assertEqual(self.status_monitor.last_change_by, "startup", "Status monitor is at startup")
        self.assertNotEqual(self.status_monitor.status, Status.SCANNING, "Status monitor does not report SCANNING at startup")

        # When: the monitored file logs that miniDLNA is now scanning
        with open(os.path.dirname(__file__) + "/../testresources/minidlnaLogFile_scanning.log") as new_log_file:
            new_log_file_contents = new_log_file.read()
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_file_contents)
            testfile.flush()

        # Then: the status monitor reports that Pelican is SCANNING
        wait() \
            .with_description("Waiting for status to change") \
            .poll_interval(1, SECOND) \
            .at_most(5, SECOND) \
            .until(lambda: self.status_monitor.last_change_by != "startup")
        self.assertEqual(self.status_monitor.status, Status.SCANNING)

        # Teardown
        self.minidlna_log_monitor.stop()


if __name__ == "__main__":
    unittest.main()
