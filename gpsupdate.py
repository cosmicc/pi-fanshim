#!/usr/bin/env python3

import subprocess
from time import sleep

import gps
import maidenhead as mh
from tzwhere import tzwhere

gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
tz = tzwhere.tzwhere()

while True:
    report = gpsd.next()
    if report['class'] == 'TPV':
        lat = getattr(report, 'lat', 0.0)
        lon = getattr(report, 'lon', 0.0)
        mhead = mh.toMaiden(lat, lon, precision=4)
        # print(f'lat: {lat}, lon: {lon}, maiden: {mhead}, {tz.tzNameAt(lat, lon)}')
        fan_file = open("/dev/shm/gps", 'w')
        print(type(lat))
        ntz = tz.tzNameAt((lat // 0.0001 / 10), (lon // 0.0001 / 10))
        fan_file.write(f'lat={lat}\nlon={lon}\nmaiden={mhead}\ntimezone={ntz}\n')
        tz_file = open("/etc/timezone", 'r')
        ctz = tz_file.read().strip('\n')
        if ctz != ntz:
            print(f'Timezone changed from {ctz} to {ntz}')
            subprocess.run(['timedatectl', 'set-timezone', ntz])
        sleep(30)
