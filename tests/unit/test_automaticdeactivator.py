import datetime
import os
import sys
import time
import unittest
from unittest.mock import Mock

from pubsub import pub
from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))

from statusmonitor import Status, StatusMonitor
from automaticdeactivator import AutomaticDeactivator


class TestStatusMonitor(unittest.TestCase):
    TEST_TIMEOUT = 1

    def setUp(self):
        self.command_executor = Mock()
        self.automatic_deactivator = AutomaticDeactivator(self.command_executor, Mock(), timeout_seconds=self.TEST_TIMEOUT)
        self.log_capture = LogCapture()
        self.status_change_messages = []
        pub.subscribe(self._save_status_change_message, StatusMonitor.TOPIC)

    def _save_status_change_message(self, status=None, changed_by=None, scheduled_deactivation=None):
        new_message = {}
        if status:
            new_message["status"] = status
        if changed_by:
            new_message["changed_by"] = changed_by
        if scheduled_deactivation:
            new_message["scheduled_deactivation"] = scheduled_deactivation
        self.status_change_messages.append(new_message)

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_deactivate_called_after_timeout(self):
        time.sleep(self.TEST_TIMEOUT + 1)
        self.command_executor.deactivate.assert_called_with()
        self.assertIn({"status": Status.DEACTIVATED, "changed_by": "automatic_deactivator"}, self.status_change_messages)
        self.log_capture.check_present(
            ("root", "INFO", "Automatic deactivation triggered.")
        )

    def test_timer_resets_correctly(self):
        time.sleep(self.TEST_TIMEOUT / 2)  # Before original timeout
        scheduled_deactivation = self.automatic_deactivator.reset_timer()
        time_of_reset = datetime.datetime.now()
        time.sleep((self.TEST_TIMEOUT / 2) + 0.1)  # Shortly after time of original timeout
        self.command_executor.deactivate.assert_not_called()
        time.sleep(self.TEST_TIMEOUT)  # After waiting for a new timeout period
        self.command_executor.deactivate.assert_called_with()
        self.assertIn({"status": Status.DEACTIVATED, "changed_by": "automatic_deactivator"}, self.status_change_messages)
        self.log_capture.check_present(
            ('root', 'INFO', 'Timer initialised.'),
            ('root', 'INFO', 'Automatic deactivation triggered.')
        )
        self.assertGreaterEqual(scheduled_deactivation,
                                time_of_reset
                                + datetime.timedelta(seconds=self.TEST_TIMEOUT)
                                - datetime.timedelta(seconds=self.TEST_TIMEOUT / 2),
                                "Returns a time near the current time plus timeout")

    def test_timer_resets_with_custom_timeout_correctly(self):
        time.sleep(self.TEST_TIMEOUT / 2)  # Before original timeout
        self.command_executor.deactivate.assert_not_called()
        self.automatic_deactivator.reset_timer(self.TEST_TIMEOUT / 10)  # Set minimal new timeout
        time.sleep(self.TEST_TIMEOUT + (self.TEST_TIMEOUT / 5))  # After new timeout but before original timeout
        self.command_executor.deactivate.assert_called_with()
        self.assertIn({"status": Status.DEACTIVATED, "changed_by": "automatic_deactivator"}, self.status_change_messages)
        self.log_capture.check_present(  # TODO: Revert back to .check()
            ('root', 'INFO', 'Timer initialised.'),
            ('root', 'INFO', 'Automatic deactivation triggered.')
        )


if __name__ == "__main__":
    unittest.main()
