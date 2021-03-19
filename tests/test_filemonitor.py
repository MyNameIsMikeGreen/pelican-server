import os
import sys
import unittest

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
        ("[2021/03/15 18:57:03] scanner.c:730: warn: Scanning /mypath", Status.SCANNING),
        ("[2021/03/15 19:02:09] scanner.c:819: warn: Scanning /mypath finished (2 files)!", Status.NOT_SCANNING),
        ("Miscellaneous log line", Status.NOT_SCANNING)
    )
    def test_monitor_detects_log_file_changes(self, new_log_line, expected_status):
        # Given: we monitor the output topic for changes
        self.topic_messages = []
        pub.subscribe(self._read_topic, StatusMonitor.TOPIC)

        # And: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # When: the monitored file is modified
        with open(TEST_FILE, "w") as testfile:
            testfile.write(new_log_line)
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

    def _read_topic(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.topic_messages.append((status, changed_by, scheduled_deactivation))


if __name__ == "__main__":
    unittest.main()
