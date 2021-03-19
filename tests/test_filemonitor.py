import os
import sys
import unittest

from busypie import wait, SECOND
from pubsub import pub

from filemonitor import MinidlnaLogMonitor
from statusmonitor import StatusMonitor, Status

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))


class TestStatusMonitor(unittest.TestCase):

    def setUp(self):
        self.test_file = "testfile"  # TODO: Get tempfile working with watchdog
        self.messages_on_topic = 0
        pub.subscribe(self._read_topic, StatusMonitor.TOPIC)
        self.minidlna_log_monitor = MinidlnaLogMonitor(self.test_file)

    def tearDown(self):
        self.minidlna_log_monitor.stop()

    def test_monitor_detects_file_changes(self):
        # Given: the file monitor is started
        self.minidlna_log_monitor.start()

        # When: the monitored file is modified
        with open(self.test_file, "w") as testfile:
            testfile.write(".")

        # Then: the monitor publishes a message to the topic
        wait()\
            .with_description("Waiting for message to appear on topic")\
            .poll_interval(1, SECOND)\
            .at_most(500, SECOND)\
            .until(lambda: self.messages_on_topic > 0)
        self.assertEqual(1, self.messages_on_topic, "One message was placed on the topic")


    def _read_topic(self, status: Status, changed_by="http_request", scheduled_deactivation=None):
        self.messages_on_topic += 1


if __name__ == "__main__":
    unittest.main()
