import json
import subprocess


def activate():
    with open("config/partitions.json") as partitions_file:
        partitions = json.load(partitions_file)
    for mapping in partitions:
        _mount(mapping["partition"], mapping["mountPoint"])
    _start_minidlna()


def deactivate():
    _stop_minidlna()
    _unmount("/dev/sda")    # TODO: Remove hardcoded device


def _mount(device, mount_point):
    subprocess.check_call("sudo mount {device} {mount_point}".format(device=device, mount_point=mount_point))


def _unmount(device, retries_count=5):
    for i in range(0, retries_count):
        try:
            subprocess.check_call("sudo eject {device}".format(device=device))
        except subprocess.CalledProcessError:
            continue
        break


def _start_minidlna():
    subprocess.check_call("sudo service minidlna restart")
    subprocess.check_call("minidlnad -R")


def _stop_minidlna():
    subprocess.check_call("sudo service minidlna stop")
