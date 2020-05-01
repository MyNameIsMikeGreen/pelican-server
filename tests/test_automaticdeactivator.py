import time
import unittest
from unittest.mock import Mock

from automaticdeactivator import AutomaticDeactivator


class TestStatusMonitor(unittest.TestCase):

    TEST_TIMEOUT = 1

    def setUp(self):
        self.status_monitor = Mock()
        self.command_executor = Mock()
        self.automatic_deactivator = AutomaticDeactivator(self.command_executor,
                                                          self.status_monitor,
                                                          timeout_seconds=self.TEST_TIMEOUT)

    def test_deactivate_called_after_timeout(self):
        time.sleep(self.TEST_TIMEOUT+1)
        self.command_executor.deactivate.assert_called()
        self.status_monitor.set_active.assert_called_with(False, changed_by="automatic_deactivator")

    def test_timer_resets_correctly(self):
        time.sleep(self.TEST_TIMEOUT / 2)   # Before original timeout
        self.automatic_deactivator.reset_timer()
        time.sleep((self.TEST_TIMEOUT / 2) + 0.1)   # Shortly after time of original timeout
        self.command_executor.deactivate.assert_not_called()
        self.status_monitor.set_active.assert_not_called()
        time.sleep(self.TEST_TIMEOUT)   # After waiting for a new timeout period
        self.command_executor.deactivate.assert_called()
        self.status_monitor.set_active.assert_called_with(False, changed_by="automatic_deactivator")


if __name__ == "__main__":
    unittest.main()
