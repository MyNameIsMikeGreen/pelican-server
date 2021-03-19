import os
import sys
import unittest

from testfixtures import LogCapture

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/')))

from commands import CommandExecutor

DUMMY_MOUNT_POINT = os.path.dirname(__file__) + "/../testresources/dummyMountPoint"


class TestCommandExecutor(unittest.TestCase):

    def setUp(self):
        device_config_file_path = self._populate_device_config_file(
            os.path.dirname(__file__) + "/../testresources/devicesTemplate.json",
            DUMMY_MOUNT_POINT
        )
        self.command_executor = CommandExecutor(device_config_file_path)
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

    def _populate_device_config_file(self, template_file_path, mount_point):
        with open(template_file_path) as template_file:
            template = template_file.read()
        contents = template.replace("${MOUNT_POINT}", mount_point)
        config_file_path = os.path.dirname(template_file_path) + "/devices.json"
        with open(config_file_path, "w") as config_file:
            config_file.write(contents)
        return config_file_path
