#!/usr/bin/env python3

import subprocess
from time import sleep

import gpsdshm
import maidenhead as mh
from tzwhere import tzwhere

gpsd_shm = gpsdshm.Shm()
tz = tzwhere.tzwhere()


def trunc(f_number, n_decimals):
    strFormNum = "{0:." + str(n_decimals + 5) + "f}"
    trunc_num = float(strFormNum.format(f_number)[:-5])
    return(trunc_num)

def get_pps():
    process = subprocess.run(['ntpq','-p'], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout.split('\n')
    for line in output:
        if len(line) > 0:
            if line[0] == "*":
                a = ' '.join(line.split())
                return a.split(' ')[1].replace('.', '')


while True:
    try:
        lat = gpsd_shm.fix.latitude
    except:
        lat is None
    try:
        lon = gpsd_shm.fix.longitude
    except:
        lon is None
    fmode = gpsd_shm.fix.mode
    if fmode == 0:
        fixmode = 'No GPS'
    if fmode == 1:
        fixmode = 'No Fix'
    if fmode == 2:
        fixmode = '2D Fix'
    if fmode == 3:
        fixmode = '3D Fix'
    if lat is not None and lon is not None:
        mhead = mh.toMaiden(lat, lon, precision=4)
        # print(f'lat: {lat}, lon: {lon}, maiden: {mhead}, {tz.tzNameAt(lat, lon)}')
        fan_file = open("/dev/shm/gps", 'w')
        ntz = tz.tzNameAt(lat, lon)
        fan_file.write(f'lat={trunc(lat, 6)}\nlon={trunc(lon, 6)}\nmaiden={mhead}\ntimezone={ntz}\nfix={fixmode}\ntimesource={get_pps()}\n')
        fan_file.close()
        tz_file = open("/etc/timezone", 'r')
        ctz = tz_file.read().strip('\n')
        tz_file.close()
        if ctz != ntz:
            print(f'Timezone changed from {ctz} to {ntz}')
            subprocess.run(['timedatectl', 'set-timezone', ntz])
        sleep(30)
    else:
        tz_file = open("/etc/timezone", 'r')
        ctz = tz_file.read().strip('\n')
        tz_file.close()
        fan_file = open("/dev/shm/gps", 'w')
        fan_file.write(f'lat=0\nlon=0\nmaiden="N/A"\ntimezone={ctz}\nfix={fixmode}\ntimesource={get_pps()}\n')
        fan_file.close()
        sleep(10)
