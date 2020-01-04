#!/usr/bin/env python3

import time

import gps
import maidenhead as mh

gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)

while True:
    report = gpsd.next()
    if report['class'] == 'TPV':
        lat = gps.getattr(report, 'lat', 0.0)
        lon = gps.getattr(report, 'lon', 0.0)
        mhead = mh.toMaiden(lat, lon, 4)
        print(f'lat: {lat}, lon: {lon}, maiden: {mhead}')
    time.sleep(10)
