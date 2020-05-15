import os
import sys
import time
import unittest
from unittest.mock import Mock

from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

from automaticdeactivator import AutomaticDeactivator


class TestStatusMonitor(unittest.TestCase):
    TEST_TIMEOUT = 1

    def setUp(self):
        self.status_monitor = Mock()
        self.command_executor = Mock()
        self.automatic_deactivator = AutomaticDeactivator(self.command_executor,
                                                          self.status_monitor,
                                                          timeout_seconds=self.TEST_TIMEOUT)
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    def test_deactivate_called_after_timeout(self):
        time.sleep(self.TEST_TIMEOUT + 1)
        self.command_executor.deactivate.assert_called_with()
        self.status_monitor.set_active.assert_called_with(False, changed_by="automatic_deactivator")
        self.log_capture.check(
            ("root", "INFO", "Automatic deactivation triggered.")
        )

    def test_timer_resets_correctly(self):
        time.sleep(self.TEST_TIMEOUT / 2)  # Before original timeout
        self.automatic_deactivator.reset_timer()
        time.sleep((self.TEST_TIMEOUT / 2) + 0.1)  # Shortly after time of original timeout
        self.command_executor.deactivate.assert_not_called()
        self.status_monitor.set_active.assert_not_called()
        time.sleep(self.TEST_TIMEOUT)  # After waiting for a new timeout period
        self.command_executor.deactivate.assert_called_with()
        self.status_monitor.set_active.assert_called_with(False, changed_by="automatic_deactivator")
        self.log_capture.check(
            ('root', 'INFO', 'Timer initialised.'),
            ('root', 'INFO', 'Automatic deactivation triggered.')
        )

    def test_timer_resets_with_custom_timeout_correctly(self):
        time.sleep(self.TEST_TIMEOUT / 2)  # Before original timeout
        self.command_executor.deactivate.assert_not_called()
        self.automatic_deactivator.reset_timer(self.TEST_TIMEOUT / 10)  # Set minimal new timeout
        time.sleep(self.TEST_TIMEOUT + (self.TEST_TIMEOUT / 5))  # After new timeout but before original timeout
        self.command_executor.deactivate.assert_called_with()
        self.status_monitor.set_active.assert_called_with(False, changed_by="automatic_deactivator")
        self.log_capture.check(
            ('root', 'INFO', 'Timer initialised.'),
            ('root', 'INFO', 'Automatic deactivation triggered.')
        )


if __name__ == "__main__":
    unittest.main()
