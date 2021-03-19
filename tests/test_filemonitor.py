import os
import sys
import unittest

from busypie import wait, SECOND
from pubsub import pub

from filemonitor import MinidlnaLogMonitor
from statusmonitor import StatusMonitor, Status

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

TEST_FILE = "testfile"


class TestStatusMonitor(unittest.TestCase):

    def test_monitor_detects_file_changes(self):

        # Given: we monitor the output topic for changes
        self.messages_on_topic = 0
        pub.subscribe(self._read_topic, StatusMonitor.TOPIC)

        # And: the file monitor is started
        self.minidlna_log_monitor = MinidlnaLogMonitor(TEST_FILE)
        self.minidlna_log_monitor.start()

        # When: the monitored file is modified
        with open(TEST_FILE, "w") as testfile:
            testfile.write(".")
            testfile.flush()

        # Then: the monitor publishes a message to the topic
        wait()\
            .with_description("Waiting for message to appear on topic")\
            .poll_interval(1, SECOND)\
            .at_most(5, SECOND)\
            .until(lambda: self.messages_on_topic > 0)
        self.assertEqual(1, self.messages_on_topic, "One message was placed on the topic")

        # Teardown
        self.minidlna_log_monitor.stop()

    def _read_topic(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.messages_on_topic += 1


if __name__ == "__main__":
    unittest.main()
