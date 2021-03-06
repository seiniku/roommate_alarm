#!/usr/bin/python
"""This script monitors for an IP address and flashes one light in the bedroom
depending on which lights are available."""
import subprocess
import time
from datetime import datetime, timedelta
from phue import Bridge
import logging
logging.basicConfig()


class NetworkDevice(object):
    """ A network device to watch for """
    def __init__(self, name, ip, color):
        self.name = name
        self.ip = ip
        self.last_seen = datetime.now() - timedelta(days=1)
        self.color = color

    def get_ip(self):
        """ returns object's ip """
        return self.ip

    def get_last_seen(self):
        """ returns object's last_seen time """
        return self.last_seen


def find_a_light():
    """Finds an appropriate light and returns it."""

    hue = Bridge('192.168.1.11')
    # If running for the first time:
    # press button on bridge and run with b.connect() uncommented
    # b.connect()

    lights = hue.get_light_objects('name')

    # reachable is supposed to be an option but isn't..?
    # if lights['Bedroom ceiling'].reachable:
    if (hue.get_light('Bedroom ceiling')['state']['reachable'] and
            hue.get_light('Bedroom ceiling')['state']['on']):
        alert_light = lights['Bedroom ceiling']

    elif (hue.get_light('Bedroom bed')['state']['reachable'] and
            hue.get_light('Bedroom bed')['state']['on']):
        alert_light = lights['Bedroom bed']

    elif hue.get_light('Bedroom desk')['state']['reachable']:
        alert_light = lights['Bedroom desk']

    return alert_light


def alert_the_light(alert_light, color):
    """Flashes a light."""
    number_of_flashes = 2
    flash_delay = 1  # seconds
    transition_time = 30  # deciseconds

    # Backup the lights configuration so that it can be stored again later.
    on_backup = alert_light.on
    hue_backup = alert_light.hue
    xy_backup = alert_light.xy
    brightness_backup = alert_light.brightness
    transition_backup = alert_light.transitiontime

    # If the light is already on, lets make it bright.
    if alert_light.on:
        min_brightness = 25
        max_brightness = 240
    else:
        min_brightness = 2
        max_brightness = 50

    # Make sure the light is on, set it to red,
    # and set the transition time.
    alert_light.on = True
    alert_light.brightness = min_brightness
    alert_light.xy = color
    alert_light.transitiontime = transition_time

    # Flash it!
    for _ in range(number_of_flashes):
        alert_light.brightness = min_brightness
        time.sleep(transition_time/10+flash_delay)
        alert_light.brightness = max_brightness
        time.sleep(transition_time/10+flash_delay)

    # Set the light back to the original configuration.
    if on_backup:
        alert_light.hue = hue_backup
        alert_light.xy = xy_backup
        alert_light.brightness = brightness_backup
        alert_light.transitiontime = transition_backup
    else:
        alert_light.transitiontime = None
        alert_light.on = on_backup


def check_for_ip(device):
    """Pings an ip and returns network_device object
       with an updated last_seen property.
    """
    ping = subprocess.call("ping -c 1 -w 1 " + device.ip + " > /dev/null 2>&1",
                           shell=True)
    if ping == 0:
        now = datetime.now()
        if (now - device.last_seen) > timedelta(minutes=15):
            light = find_a_light()
            if light is not None:
                print ("ALERT! - " +
                       now.strftime("%Y-%m-%d %H:%M") + " - " +
                       device.name + " - " + light.name)
                alert_the_light(light, device.color)
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

    jason = NetworkDevice("jason",
                          "192.168.1.250",
                          colors['firebrick'])
    justin = NetworkDevice("justin",
                           "192.168.1.251",
                           colors['orchid'])

    # This is the main business loop, clearly.
    while True:
        justin = check_for_ip(justin)
        jason = check_for_ip(jason)
        time.sleep(3)

if __name__ == "__main__":
    main()
