#!/usr/bin/env python3
from fanshim import FanShim
from threading import Lock
import colorsys
import psutil
import argparse
import time
import signal
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--threshold', type=float, default=-1, help='Temperature threshold in degrees C to enable fan')
parser.add_argument('--hysteresis', type=float, default=-1, help='Distance from threshold before fan is disabled')

parser.add_argument('--off-threshold', type=float, default=55.0, help='Temperature threshold in degrees C to enable fan')
parser.add_argument('--on-threshold', type=float, default=65.0, help='Temperature threshold in degrees C to disable fan')
parser.add_argument('--delay', type=float, default=2.0, help='Delay, in seconds, between temperature readings')
parser.add_argument('--preempt', action='store_true', default=False, help='Monitor CPU frequency and activate cooling premptively')
parser.add_argument('--verbose', action='store_true', default=False, help='Output temp and fan status messages')
parser.add_argument('--nobutton', action='store_true', default=False, help='Disable button input')
parser.add_argument('--noled', action='store_true', default=False, help='Disable LED control')
parser.add_argument('--brightness', type=float, default=255.0, help='LED brightness, from 0 to 255')

args = parser.parse_args()


def clean_exit(signum, frame):
    set_fan(False)
    if not args.noled:
        fanshim.set_light(0, 0, 0)
    sys.exit(0)


def update_led_temperature(temp):
    led_busy.acquire()
    temp = float(temp)
    temp -= args.off_threshold
    temp /= float(args.on_threshold - args.off_threshold)
    temp = max(0, min(1, temp))
    temp = 1.0 - temp
    temp *= 120.0
    temp /= 360.0
    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(temp, 1.0, args.brightness / 255.0)]
    fanshim.set_light(r, g, b)
    led_busy.release()


def get_cpu_temp():
    t = psutil.sensors_temperatures()
    for x in ['cpu-thermal', 'cpu_thermal']:
        if x in t:
            temp_file = open("/dev/shm/cputemp", 'w')
            temp_file.write(t[x][0].current)
            return t[x][0].current
    print("Warning: Unable to get CPU temperature!")
    return 0


def get_cpu_freq():
    freq = psutil.cpu_freq()
    freq_file = open("/dev/shm/cpufreq", 'w')
    freq_file.write(freq)
    return freq


def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
        fanshim.set_fan(status)
        fan_file = open("/dev/shm/fan", 'w')
        fan_file.write(status)
    enabled = status
    return changed


if args.threshold > -1 or args.hysteresis > -1:
    print("""
The --threshold and --hysteresis parameters have been deprecated.
Use --on-threshold and --off-threshold instead!
""")
    sys.exit(1)


fanshim = FanShim()
fanshim.set_hold_time(1.0)
fanshim.set_fan(False)
armed = True
enabled = False
led_busy = Lock()
enable = False
is_fast = False
last_change = 0
signal.signal(signal.SIGTERM, clean_exit)
file_started_flag = False
file_log_every_few = 10

t = get_cpu_temp()
if t >= args.threshold:
    last_change = get_cpu_temp()
    set_fan(True)


if not args.nobutton:
    @fanshim.on_release()
    def release_handler(was_held):
        global armed
        if was_held:
            pass
            # set_automatic(not armed)
        elif not armed:
            set_fan(not enabled)

    @fanshim.on_hold()
    def held_handler():
        global led_busy
        if args.noled:
            return
        led_busy.acquire()
        for _ in range(3):
            fanshim.set_light(0, 0, 255)
            time.sleep(0.04)
            fanshim.set_light(0, 0, 0)
            time.sleep(0.04)
        led_busy.release()


try:
    while True:
        t = get_cpu_temp()
        f = get_cpu_freq()
        was_fast = is_fast
        is_fast = (int(f.current) == int(f.max))
        if armed:
            # if args.verbose:
            #    print("check")
            if t >= args.on_threshold:
                # if args.verbose:
                #    print("on")
                enable = True
            elif t <= args.off_threshold:
                # if args.verbose:
                #    print("off")
                enable = False
        if not args.noled:
            update_led_temperature(t)
        if args.preempt and is_fast and was_fast:
            enable = True
        if set_fan(enable):
            last_change = t
        if args.verbose:
            print("Current: {:05.02f}  Targets: {:05.02f} to {:05.02f}  Freq {: 5.02f}  Automatic: {}  Fan On: {}".format(t, args.off_threshold, args.on_threshold, f.current / 1000.0, armed, enabled))
            log_line = str(t) + "," + str(args.off_threshold) + "/" + str(args.on_threshold) + "," + str(f.current / 1000.0) + "," + str(armed) + "," + str(enabled) + "\n"
            if not(file_started_flag):
                file_started_flag = True
                log_file = open("/var/log/fanshim.log", 'w')
                log_file.write("Current Temp,Target Temp,CPU Freq,Automatic,Fan State \n")
            if file_log_every_few >= 10:
                log_file.write(log_line)
                file_log_every_few = 0
                log_file.flush()
            else:
                file_log_every_few += 1
        time.sleep(args.delay)
except KeyboardInterrupt:
    pass
