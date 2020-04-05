import json
import subprocess


def activate():
    partitions = json.load("config/partitions.json")
    for mapping in partitions:
        _mount(mapping["partition"], mapping["mountPoint"])
    _start_minidlna()


def deactivate():
    _stop_minidlna()
    _unmount(f"/dev/sda")


def _mount(device, mount_point):
    subprocess.check_call(f"sudo mount {device} {mount_point}")


def _unmount(device, retries_count=5):
    for i in range(0, retries_count):
        subprocess.check_call(f"sudo eject {device}")


def _start_minidlna():
    subprocess.check_call("sudo service minidlna restart")
    subprocess.check_call("minidlnad -R")


def _stop_minidlna():
    subprocess.check_call("sudo service minidlna stop")
