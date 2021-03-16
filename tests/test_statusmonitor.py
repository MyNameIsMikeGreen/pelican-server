import os
import sys
import unittest

from pubsub import pub
from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

from statusmonitor import StatusMonitor, Status


class TestStatusMonitor(unittest.TestCase):

    def setUp(self):
        self.status_monitor = StatusMonitor()
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_status_monitor_deactivated_by_default(self):
        self.assertEqual(Status.DEACTIVATED, self.status_monitor.status)

    def test_status_monitor_status_changes_successfully(self):
        original_timestamp = self.status_monitor.last_change
        changed_by_string = "test"
        scheduled_deactivation_string = "test2"
        new_status = Status.ACTIVATED
        pub.sendMessage(StatusMonitor.TOPIC, status=new_status, changed_by=changed_by_string, scheduled_deactivation=scheduled_deactivation_string)
        self.assertEqual(new_status, self.status_monitor.status)
        self.assertGreater(self.status_monitor.last_change, original_timestamp)
        self.assertEqual(self.status_monitor.last_change_by, changed_by_string)
        self.assertEqual(self.status_monitor.scheduled_deactivation, scheduled_deactivation_string)
        # self.log_capture.check( TODO: Investigate double logging bug
        #     ("root", "INFO", "New status: " + new_status.name + ".")
        # )


if __name__ == "__main__":
    unittest.main()
