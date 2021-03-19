import os
import sys
import unittest
from time import sleep

from ddt import ddt, data, unpack
from busypie import wait, SECOND
from pubsub import pub

from filemonitor import MinidlnaLogMonitor
from statusmonitor import StatusMonitor, Status

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

TEST_FILE = "testfile"


@ddt
class TestStatusMonitor(unittest.TestCase):

    @unpack
    @data(
        ("minidlnaLogFile_scanning.log", Status.SCANNING),
        ("minidlnaLogFile_notScanning.log", Status.NOT_SCANNING)
    )
    def test_monitor_fires_event_if_scan_state_change_detected(self, log_file, expected_status):
        # Given: we monitor the output topic for changes
        self.topic_messages = []
        pub.subscribe(self._read_topic, StatusMonitor.TOPIC)

        # And: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # When: the monitored file is modified
        with open(os.path.dirname(__file__) + "/testresources/" + log_file) as new_log_file:
            new_log_file_contents = new_log_file.read()
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_file_contents)
            testfile.flush()

        # Then: the monitor publishes a message to the topic
        wait() \
            .with_description("Waiting for message to appear on topic") \
            .poll_interval(1, SECOND) \
            .at_most(5, SECOND) \
            .until(lambda: len(self.topic_messages) > 0)
        self.assertEqual(1, len(self.topic_messages), "One message was placed on the topic")
        self.assertEqual(expected_status, self.topic_messages[0][0], "Message contains correct status")

        # Teardown
        self.minidlna_log_monitor.stop()
        pub.unsubAll()

    def test_monitor_does_not_fire_event_if_file_updates_but_insufficient_information(self):
        # Given: we monitor the output topic for changes
        self.topic_messages = []
        pub.subscribe(self._read_topic, StatusMonitor.TOPIC)

        # And: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # When: the monitored file is modified
        with open(os.path.dirname(__file__) + "/testresources/minidlnaLogFile_miscellaneous.log") as new_log_file:
            new_log_file_contents = new_log_file.read()
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_file_contents)
            testfile.flush()

        # Then: no message appears on the topic
        sleep(5)  # Allow time for message to appear
        self.assertListEqual([], self.topic_messages, "No messages were places on the topic")

        # Teardown
        self.minidlna_log_monitor.stop()
        pub.unsubAll()

    def _read_topic(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.topic_messages.append((status, changed_by, scheduled_deactivation))


if __name__ == "__main__":
    unittest.main()
