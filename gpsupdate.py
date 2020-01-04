#!/usr/bin/env python3

import time
from tzwhere import tzwhere
import gps
import maidenhead as mh

gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
tz = tzwhere.tzwhere()

while True:
    report = gpsd.next()
    if report['class'] == 'TPV':
        lat = getattr(report, 'lat', 0.0)
        lon = getattr(report, 'lon', 0.0)
        mhead = mh.toMaiden(lat, lon, precision=4)
        print(f'lat: {lat}, lon: {lon}, maiden: {mhead}, {tz.tzNameAt(lat, lon)}')
        time.sleep(10)
