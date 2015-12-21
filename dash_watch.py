#!/usr/bin/python
"""This script monitors for an IP address and flashes one light in the bedroom
depending on which lights are available."""
import subprocess
from datetime import datetime, timedelta
from qhue import Bridge
import logging
logging.basicConfig()


class NetworkDevice(object):
    """ A network device to watch for """
    def __init__(self, name, ip, color, group_name):
        self.name = name
        self.ip = ip
        self.last_seen = datetime.now() - timedelta(days=1)
        self.color = color
        self.group_name = group_name

    def get_ip(self):
        """ returns object's ip """
        return self.ip

    def get_last_seen(self):
        """ returns object's last_seen time """
        return self.last_seen


def find_a_light(hue, group_name):
    """Finds an appropriate light and returns it."""

    hue = Bridge('192.168.1.11', "newdeveloper")
    # hue(devicetype="test user", username="newdeveloper", http_method="post")
    groups = hue.groups()
    for item in groups:
        item_name = hue.groups(item)["name"]
        if item_name == group_name:
            lights = hue.groups(item)["lights"]
            break
    return lights


def should_turn_on(hue, lights):
    """ returns true of the lights should be turned on """
    should_power_on = True
    for item in lights:
        if hue.lights(item)["state"]["on"]:
            should_power_on = False
            break
    return should_power_on


def toggle_lights(hue, lights, should_power_on):
    """ toggles lights to should_power_on state """
    print should_power_on
    for item in lights:
        hue.lights[item].state(on=should_power_on)


def check_for_ip(device):
    """Pings an ip and returns network_device object
       with an updated last_seen property.
    """
    ping = subprocess.call("ping -c 1 -w 1 " + device.ip + " > /dev/null 2>&1",
                           shell=True)
    hue = Bridge('192.168.1.11', "newdeveloper")
    if ping == 0:
        now = datetime.now()
        if (now - device.last_seen) > timedelta(seconds=15):
            light = find_a_light(hue, device.group_name)
            toggle_lights(hue, light, should_turn_on(hue, light))
            if light is not None:
                print ("ALERT! - " +
                       now.strftime("%Y-%m-%d %H:%M") + " - " +
                       device.name)
            device.last_seen = now
    return device


def main():
    """Initiates the checking of an ip and tracks the time the device
    was last seen on the network. runs until cancelled by user.
    """

    # More color values can be found at
    # http://www.developers.meethue.com/documentation/hue-xy-values
    colors = dict()
    colors['firebrick'] = [0.6621, .3023]
    colors['dark_blue'] = [0.139, 0.081]
    colors['orchid'] = [0.3365, 0.1735]
    colors['olive'] = [0.4432, 0.5154]
    colors['yellow'] = [0.4432, 0.5154]
    colors['violet'] = [0.3644, 0.2133]

    glad = NetworkDevice("glad",
                         "glad.bad.wolf",
                         colors['firebrick'],
                         "Basement")

    tide = NetworkDevice("tide",
                         "tide.bad.wolf",
                         colors['firebrick'],
                         "Basement")

    finish = NetworkDevice("finish",
                           "finish.bad.wolf",
                           colors['firebrick'],
                           "Bedroom_all")

    ziploc = NetworkDevice("ziploc",
                           "ziploc.bad.wolf",
                           colors['firebrick'],
                           "Bedroom_all")

    # This is the main business loop, clearly.
    while True:
        try:
            glad = check_for_ip(glad)
            tide = check_for_ip(tide)
            finish = check_for_ip(finish)
            ziploc = check_for_ip(ziploc)
        except KeyboardInterrupt:
            print "Quiting.."
            exit()
if __name__ == "__main__":
    main()
