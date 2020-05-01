import os
import sys
import unittest

from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

from statusMonitor import StatusMonitor, Status


class TestStatusMonitor(unittest.TestCase):

    def setUp(self):
        self.status_monitor = StatusMonitor()
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_status_monitor_deactivated_by_default(self):
        self.assertEqual(Status.DEACTIVATED, self.status_monitor.status)

    def test_status_monitor_activated_when_set_active_set_to_true(self):
        original_timestamp = self.status_monitor.last_change
        changed_by_string = "activation_test"
        self.status_monitor.set_active(True, changed_by=changed_by_string)
        self.assertEqual(Status.ACTIVATED, self.status_monitor.status)
        self.assertGreater(self.status_monitor.last_change, original_timestamp)
        self.assertEqual(self.status_monitor.last_change_by, changed_by_string)
        self.log_capture.check(
            ("root", "INFO", "New status: ACTIVATED.")
        )

    def test_status_monitor_activated_when_set_active_set_to_false(self):
        original_timestamp = self.status_monitor.last_change
        changed_by_string = "deactivation_test"
        self.status_monitor.set_active(False, changed_by=changed_by_string)
        self.assertEqual(Status.DEACTIVATED, self.status_monitor.status)
        self.assertGreater(self.status_monitor.last_change, original_timestamp)
        self.assertEqual(self.status_monitor.last_change_by, changed_by_string)
        self.log_capture.check(
            ("root", "INFO", "New status: DEACTIVATED.")
        )


if __name__ == "__main__":
    unittest.main()
