import json
import subprocess


class CommandExecutor:

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

    @staticmethod
    def _mount(device, mount_point):
        subprocess.check_call("sudo mount {device} {mount_point}".format(device=device, mount_point=mount_point), shell=True)

    @staticmethod
    def _unmount(device, retries_count=5):
        for i in range(0, retries_count):
            try:
                subprocess.check_call("sudo eject {device}".format(device=device), shell=True)
            except subprocess.CalledProcessError:
                continue
            break

    @staticmethod
    def _start_minidlna():
        subprocess.check_call("sudo service minidlna restart", shell=True)

    @staticmethod
    def _stop_minidlna():
        subprocess.check_call("sudo service minidlna stop", shell=True)
