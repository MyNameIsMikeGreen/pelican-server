import os
import sys
import unittest
from unittest.mock import Mock, call

from ddt import ddt, unpack, data
from pubsub import pub
from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))

from statusmonitor import StatusMonitor, Status


@ddt
class TestStatusMonitor(unittest.TestCase):

    def setUp(self):
        self.prometheus_service = Mock()
        self.status_monitor = StatusMonitor(self.prometheus_service)
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_status_monitor_deactivated_by_default(self):
        self.assertEqual(Status.DEACTIVATED, self.status_monitor.status)

    @unpack
    @data(
        (Status.ACTIVATED, 1, 0, 0, 0),
        (Status.DEACTIVATED, 0, 1, 0, 0),
        (Status.MODIFYING, 0, 0, 1, 0),
        (Status.SCANNING, 0, 0, 0, 1)
    )
    def test_status_monitor_status_changes_successfully_for_standard_status_types(self, status,
                                                                                  expected_activated_metric_value,
                                                                                  expected_deactivated_metric_value,
                                                                                  expected_modifying_metric_value,
                                                                                  expected_scanning_metric_value):
        original_timestamp = self.status_monitor.last_change
        changed_by_string = "test"
        scheduled_deactivation_string = "test2"
        pub.sendMessage(StatusMonitor.TOPIC, status=status, changed_by=changed_by_string,
                        scheduled_deactivation=scheduled_deactivation_string)
        self.assertEqual(status, self.status_monitor.status)
        self.assertGreater(self.status_monitor.last_change, original_timestamp)
        self.assertEqual(self.status_monitor.last_change_by, changed_by_string)
        self.assertEqual(self.status_monitor.scheduled_deactivation, scheduled_deactivation_string)
        self.prometheus_service.gauge.assert_has_calls([
            call("status_is_activated", expected_activated_metric_value),
            call("status_is_deactivated", expected_deactivated_metric_value),
            call("status_is_modifying", expected_modifying_metric_value),
            call("status_is_scanning", expected_scanning_metric_value)
        ], any_order=True)
        # self.log_capture.check( TODO: Investigate double logging bug
        #     ("root", "INFO", "New status: " + new_status.name + ".")
        # )

    def test_status_monitor_ignores_scan_complete_messages_if_not_scanning(self):
        original_status = self.status_monitor.status
        self.assertNotEqual(original_status, Status.SCAN_COMPLETE)
        pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCAN_COMPLETE, changed_by="", scheduled_deactivation="")
        self.assertEqual(original_status, self.status_monitor.status, "Status is unchanged")
        self.log_capture.check()  # No logs

    def test_status_monitor_status_changes_to_activated_if_scan_complete_received_while_scanning(self):
        self.status_monitor.status = Status.SCANNING
        original_timestamp = self.status_monitor.last_change
        changed_by_string = "test"
        scheduled_deactivation_string = "test2"
        pub.sendMessage(StatusMonitor.TOPIC, status=Status.SCAN_COMPLETE, changed_by=changed_by_string,
                        scheduled_deactivation=scheduled_deactivation_string)

        self.assertEqual(Status.ACTIVATED, self.status_monitor.status)
        self.assertGreater(self.status_monitor.last_change, original_timestamp)
        self.assertEqual(self.status_monitor.last_change_by, changed_by_string)
        self.assertEqual(self.status_monitor.scheduled_deactivation, scheduled_deactivation_string)
        self.prometheus_service.gauge.assert_has_calls([
            call("status_is_activated", 1),
            call("status_is_deactivated", 0),
            call("status_is_modifying", 0),
            call("status_is_scanning", 0)
        ], any_order=True)
        # self.log_capture.check( TODO: Investigate double logging bug
        #     ("root", "INFO", "New status: " + new_status.name + ".")
        # )


if __name__ == "__main__":
    unittest.main()
