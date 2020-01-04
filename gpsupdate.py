#!/usr/bin/env python3

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
        fan_file.write(f'lat={lat}\nlon={lon}\nmaiden={mhead}\ntimezone={tz.tzNameAt(lat, lon)}\n')
        sleep(30)
