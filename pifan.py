#!/usr/bin/env python3
import argparse
import colorsys
import signal
import sys
import time
from threading import Lock
import subprocess
import psutil

from fanshim import FanShim

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
    temp -= 40
    temp /= float(70 - 40)
    temp = max(0, min(1, temp))
    temp = 1.0 - temp
    temp *= 120.0
    temp /= 360.0
    r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(temp, 1.0, args.brightness / 255.0)]
    fanshim.set_light(r, g, b)
    led_busy.release()


def get_cpu_temp():
    process = subprocess.run(['/opt/vc/bin/vcgencmd', 'measure_temp'], check=True, stdout=subprocess.PIPE,universal_newlines=True)
    output = process.stdout.strip().split('=')
    npft = output[1].split("'")[0]
    pft = npft.split('.')[0]
    temp_file = open("/dev/shm/cputemp", 'w')
    temp_file.write(str(pft))
    temp_file.close()
    return float(pft)


def get_cpu_freq():
    freq = psutil.cpu_freq()
    freq_file = open("/dev/shm/cpufreq", 'w')
    freq_file.write(str(int(freq.current)))
    return freq


def set_fan(status):
    global enabled
    changed = False
    if status != enabled:
        changed = True
        # fanshim.set_fan(status)
    enabled = status
    return changed


def get_fan():
    fstat = fanshim.get_fan()
    if fstat == 1:
        fst = "ON"
    else:
        fst = "OFF"
    fan_file = open("/dev/shm/fan", 'w')
    fan_file.write(fst)


if args.threshold > -1 or args.hysteresis > -1:
    print("""
The --threshold and --hysteresis parameters have been deprecated.
Use --on-threshold and --off-threshold instead!
""")
    sys.exit(1)


fanshim = FanShim()
fanshim.set_hold_time(1.0)
fanshim.set_fan(True)
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

try:
    while True:
        t = get_cpu_temp()
        f = get_cpu_freq()
        get_fan()
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
