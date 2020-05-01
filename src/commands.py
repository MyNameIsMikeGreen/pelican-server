import json
import subprocess


class CommandExecutor:

    minidlna_restart_command = "sudo service minidlna restart"
    minidlna_stop_command = "sudo service minidlna stop"
    mount_command_template = "sudo mount {device} {mount_point}"
    unmount_command_template = "sudo eject {device}"

    devices = []

    def __init__(self, devices_file_path="config/devices.json"):
        with open(devices_file_path) as devices_file:
            self.devices = json.load(devices_file)

    def activate(self):
        for device in self.devices:
            for partition in device["partitions"]:
                self._mount(partition["path"], partition["mountPoint"])
        self._start_minidlna()

    def deactivate(self):
        self._stop_minidlna()
        for device in self.devices:
            self._unmount(device["path"])

    def _mount(self, device, mount_point):
        subprocess.check_call(self.mount_command_template.format(device=device, mount_point=mount_point), shell=True)

    def _unmount(self, device, retries_count=5):
        for i in range(0, retries_count):
            try:
                subprocess.check_call(self.unmount_command_template.format(device=device), shell=True)
            except subprocess.CalledProcessError:
                continue
            break

    def _start_minidlna(self):
        subprocess.check_call(self.minidlna_restart_command, shell=True)

    def _stop_minidlna(self):
        subprocess.check_call(self.minidlna_stop_command, shell=True)
