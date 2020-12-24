import os
import sys
import unittest

from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/')))

from commands import CommandExecutor

DUMMY_MOUNT_POINT = "tests/testresources/dummyMountPoint"

class TestCommandExecutor(unittest.TestCase):

    def setUp(self):
        self.command_executor = CommandExecutor(os.path.dirname(__file__) + "/testresources/devices.json")
        null_command = ":"
        self.command_executor.minidlna_restart_command = null_command
        self.command_executor.minidlna_stop_command = null_command
        self.command_executor.minidlna_restart_command = null_command
        self.command_executor.minidlna_rescan_command = null_command
        self.command_executor.mount_command_template = null_command
        self.command_executor.unmount_command_template = null_command
        self.log_capture = LogCapture()

    def tearDown(self):
        self.log_capture.uninstall_all()

    @classmethod
    def tearDownClass(cls):
        os.rmdir(DUMMY_MOUNT_POINT)

    def test_device_config_loaded_successfully(self):
        expected_device_entry = {
                "path": "/dev/sda",
                "partitions": [
                    {
                        "path": "/dev/sda1",
                        "mountPoint": DUMMY_MOUNT_POINT
                    }
                ]
            }
        self.assertEqual(1, len(self.command_executor.devices))
        self.assertDictEqual(expected_device_entry, self.command_executor.devices[0])

    def test_each_partition_mounted(self):
        self.command_executor.activate()
        self.log_capture.check(
            ("root", "INFO", f"Mounting '/dev/sda1' at '{DUMMY_MOUNT_POINT}'."),
            ("root", "INFO", "Restarting minidlna.")
        )

    def test_each_device_unmounted(self):
        self.command_executor.deactivate()
        self.log_capture.check(
            ("root", "INFO", "Stopping minidlna."),
            ("root", "INFO", "Unmounting '/dev/sda'.")
        )

    def test_library_rescanned(self):
        self.command_executor.rescan()
        self.log_capture.check(
            ("root", "INFO", "Rescanning libraries."),
            ("root", "INFO", "Restarting minidlna.")
        )
