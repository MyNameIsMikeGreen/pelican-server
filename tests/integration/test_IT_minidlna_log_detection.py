import os
import sys
import unittest
from time import sleep

from busypie import wait, SECOND

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))

from filemonitor import MinidlnaLogMonitor
from statusmonitor import StatusMonitor, Status

TEST_FILE = os.path.dirname(__file__) + "/../testresources/testfile"


class TestITDlnaLogDetection(unittest.TestCase):

    def test_status_changed_to_scanning_when_log_file_indicates_minidlna_is_scanning(self):
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

    def test_status_is_unchanged_if_log_file_indicates_minidlna_has_finished_scanning_but_status_was_not_previously_scanning(self):
        # Given: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # And: the status monitor is started
        self.status_monitor = StatusMonitor()
        self.assertEqual(self.status_monitor.last_change_by, "startup", "Status monitor is at startup")
        self.assertNotEqual(self.status_monitor.status, Status.SCANNING, "Status monitor does not report SCANNING at startup")

        # And: we record the initial status of the status monitor
        initial_status = self.status_monitor.status

        # When: the monitored file logs that miniDLNA is not scanning
        with open(os.path.dirname(__file__) + "/../testresources/minidlnaLogFile_notScanning.log") as new_log_file:
            new_log_file_contents = new_log_file.read()
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_file_contents)
            testfile.flush()

        # Then: no status change occurs
        sleep(5)  # Allow time for any status change to occur
        self.assertEqual(self.status_monitor.status, initial_status, "The status is unchanged")

        # Teardown
        self.minidlna_log_monitor.stop()

    def test_status_is_unchanged_if_log_file_contains_no_scanning_information(self):
        # Given: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # And: the status monitor is started
        self.status_monitor = StatusMonitor()

        # And: we record the initial status of the status monitor
        initial_status = self.status_monitor.status

        # When: the monitored file logs that miniDLNA is not scanning
        with open(os.path.dirname(__file__) + "/../testresources/minidlnaLogFile_miscellaneous.log") as new_log_file:
            new_log_file_contents = new_log_file.read()
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_file_contents)
            testfile.flush()

        # Then: no status change occurs
        sleep(5)  # Allow time for any status change to occur
        self.assertEqual(self.status_monitor.status, initial_status, "The status is unchanged")

        # Teardown
        self.minidlna_log_monitor.stop()


if __name__ == "__main__":
    unittest.main()
