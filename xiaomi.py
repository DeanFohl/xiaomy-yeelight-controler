#!/usr/bin/python3
# coding: utf-8

import sys
import getopt
import time
import threading
from tkinter.colorchooser import askcolor
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from yeelight import Bulb, discover_bulbs
from yeelight.flows import transitions
from yeelight import flows

# Catalogues pour animations et couleurs
COLOR_CATALOGUE = {
    "rose": (238, 130, 238),
    "violet": (238, 130, 238),
    "jaune": (255, 255, 0),
    "bleu": (0, 0, 255),
    "rouge": (255, 0, 0),
    "vert": (0, 255, 0),
    "orange": (255, 165, 0),
    "blanc": (255, 255, 255),
}

STANDARD_ANIMATIONS = [
    "disco", "temp", "strobe", "pulse", "strobe_color", "alarm", "police",
    "police2", "lsd", "christmas", "rgb", "random_loop", "slowdown", "home",
    "night_mode", "date_night", "movie", "sunrise", "sunset", "romance",
    "happy_birthday", "candle_flicker", "tea_time"
]

class Color:
    def __init__(self, r, g, b, brightness=100):
        self.r = r
        self.g = g
        self.b = b
        self.brightness = brightness

class Animation:
    def __init__(self, events=None, repetition=1, effect=''):
        self.events = events or []
        self.repetition = repetition
        self.effect = effect

    def play(self, bulb, duration):
        timeout_start = time.time()
        while time.time() < timeout_start + duration:
            for event in self.events:
                bulb.effect = self.effect
                if event.color.r == event.color.g == event.color.b == 0:
                    bulb.toggle()
                    time.sleep(event.duration)
                    bulb.toggle()
                else:
                    bulb.set_rgb(event.color.r, event.color.g, event.color.b)
                    bulb.set_brightness(event.color.brightness)
                    time.sleep(event.duration)

class Event:
    def __init__(self, color, duration):
        self.color = color
        self.duration = duration

def adjust_intensity(color, intensity):
    intensity = max(0, min(intensity, 1))
    return RGBColor(
        int(color.r * intensity),
        int(color.g * intensity),
        int(color.b * intensity)
    )

def parse_arguments(argv):
    options = {
        "ip": "",
        "action": "",
        "scenario": "",
        "brightness": "",
        "color": "",
        "name": "",
        "duration": 5,
        "pc": False,
        "cp": False,
    }

    short_opts = "i:a:s:l:c:n:d:phc"
    long_opts = [
        "ip=", "action=", "scenario=", "brightness=", "color=", "name=",
        "duration=", "pc", "help", "cp"
    ]

    try:
        opts, _ = getopt.getopt(argv, short_opts, long_opts)
    except getopt.GetoptError as err:
        print(err)
        display_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            display_help()
            sys.exit()
        elif opt in ("-i", "--ip"):
            options["ip"] = arg
        elif opt in ("-a", "--action"):
            options["action"] = arg
        elif opt in ("-s", "--scenario"):
            options["scenario"] = arg
        elif opt in ("-l", "--brightness"):
            options["brightness"] = arg
        elif opt in ("-c", "--color"):
            options["color"] = arg.replace(' ', '')
        elif opt in ("-n", "--name"):
            options["name"] = arg.replace(' ', '')
        elif opt in ("-d", "--duration"):
            options["duration"] = int(arg)
        elif opt in ("-p", "--pc"):
            options["pc"] = True
        elif opt == "--cp":
            options["cp"] = True

    return options

def open_color_picker():
    color = askcolor()[0]
    if color:
        r, g, b = map(int, color)
        return Color(r, g, b)
    return None

def display_help():
    print("\nUsage:")
    print("  --ip <lamp IP>")
    print("  --action <toggle/brightness+/brightness-/animation>")
    print("  --color <name/RGB>")
    print("  --brightness <0-100>")
    print("  --scenario <name of animation>")
    print("\nAvailable Colors:")
    for color in COLOR_CATALOGUE:
        print(f"  - {color}")
    print("\nStandard Animations:")
    for anim in STANDARD_ANIMATIONS:
        print(f"  - {anim}")

    print("\nDiscovering available lamps on the network...")
    try:
        bulbs = discover_bulbs(timeout=5)
        if bulbs:
            print("Available lamps:")
            for bulb in bulbs:
                print(f"  - IP: {bulb['ip']} | Model: {bulb.get('capabilities', {}).get('model', 'Unknown')}")
        else:
            print("  No lamps found on the network.")
    except Exception as e:
        print(f"Error discovering lamps: {e}")

def main():
    options = parse_arguments(sys.argv[1:])
    ip_list = options["ip"].split(",")
    bulbs = []

    for ip in ip_list:
        if ip:
            try:
                bulbs.append(Bulb(ip, auto_on=True))
            except Exception as e:
                print(f"Error connecting to bulb at {ip}: {e}")

    pc_devices = []
    if options["pc"]:
        try:
            client = OpenRGBClient()
            pc_devices = client.devices
        except Exception as e:
            print(f"Error connecting to OpenRGB: {e}")

    color = None
    if options["cp"]:
        color = open_color_picker()

    if options["color"]:
        color = parse_color(options["color"])

    if color:
        apply_color_to_devices(bulbs, pc_devices, color)

    if options["action"] == "toggle":
        toggle_devices(bulbs, pc_devices)
    elif options["action"] == "brightness+":
        adjust_brightness(bulbs, step=15)
    elif options["action"] == "brightness-":
        adjust_brightness(bulbs, step=-15)
    elif options["brightness"]:
        set_brightness(bulbs, int(options["brightness"]))
    elif options["action"] == "animation":
        play_animation(bulbs, options["scenario"], options["duration"])

def parse_color(color_str):
    if color_str in COLOR_CATALOGUE:
        r, g, b = COLOR_CATALOGUE[color_str]
    elif "," in color_str:
        r, g, b = map(int, color_str.split(","))
    else:
        raise ValueError("Invalid color format")
    return Color(r, g, b)

def apply_color_to_devices(bulbs, pc_devices, color):
    for bulb in bulbs:
        threading.Thread(target=set_bulb_color, args=(bulb, color)).start()

    for device in pc_devices:
        device.set_custom_mode()
        device.set_color(RGBColor(color.r, color.g, color.b))

def set_bulb_color(bulb, color):
    try:
        if color.r == 255 and color.g == 255 and color.b == 255:
            bulb.set_color_temp(6000)
        else:
            bulb.set_rgb(color.r, color.g, color.b)
    except Exception as e:
        print(f"Error setting color to {bulb._ip}: {e}")

def toggle_devices(bulbs, pc_devices):
    for bulb in bulbs:
        threading.Thread(target=toggle_bulb, args=(bulb,)).start()
    for device in pc_devices:
        device.off()

def toggle_bulb(bulb):
    try:
        bulb.toggle()
    except Exception as e:
        print(f"Error toggling bulb {bulb._ip}: {e}")

def adjust_brightness(bulbs, step):
    for bulb in bulbs:
        threading.Thread(target=change_brightness, args=(bulb, step)).start()

def change_brightness(bulb, step):
    try:
        bulb.effect = 'smooth'
        data = bulb.get_properties()
        current_brightness = int(data['bright'])
        new_brightness = max(20, min(100, current_brightness + step))
        bulb.set_brightness(new_brightness)
    except Exception as e:
        print(f"Error adjusting brightness for bulb {bulb._ip}: {e}")

def set_brightness(bulbs, brightness):
    for bulb in bulbs:
        try:
            bulb.set_brightness(brightness)
        except Exception as e:
            print(f"Error setting brightness for bulb {bulb._ip}: {e}")

def play_animation(bulbs, scenario, duration):
    for bulb in bulbs:
        try:
            if scenario in STANDARD_ANIMATIONS:
                exec(f"bulb.start_flow(flows.{scenario}())")
            else:
                print("Custom animations not yet supported.")
        except Exception as e:
            print(f"Error playing animation on bulb {bulb._ip}: {e}")

if __name__ == "__main__":
    main()
