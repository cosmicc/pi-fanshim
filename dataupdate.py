#!/usr/bin/env python3.8

import subprocess
from time import sleep
import urllib.request
from pathlib import Path

import gpsdshm
import maidenhead as mh
from tzwhere import tzwhere

gpsd_shm = gpsdshm.Shm()
tz = tzwhere.tzwhere()
net_file = Path('/dev/shm/network')


def trunc(f_number, n_decimals):
    strFormNum = "{0:." + str(n_decimals + 5) + "f}"
    trunc_num = float(strFormNum.format(f_number)[:-5])
    return(trunc_num)


def get_pps():
    process = subprocess.run(['ntpq', '-p'], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    output = process.stdout.split('\n')
    for line in output:
        if len(line) > 0:
            if line[0] == "*":
                a = ' '.join(line.split())
                return a.split(' ')[1].replace('.', '')


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


def remap(x, oMin, oMax, nMin, nMax):
    if oMin == oMax:
        print("Warning: Zero input range")
        return None
    if nMin == nMax:
        print("Warning: Zero output range")
        return None
    reverseInput = False
    oldMin = min(oMin, oMax)
    oldMax = max(oMin, oMax)
    if not oldMin == oMin:
        reverseInput = True
    reverseOutput = False
    newMin = min(nMin, nMax)
    newMax = max(nMin, nMax)
    if not newMin == nMin:
        reverseOutput = True
    portion = (x - oldMin) * (newMax - newMin) / (oldMax - oldMin)
    if reverseInput:
        portion = (oldMax - x) * (newMax - newMin) / (oldMax - oldMin)
    result = portion + newMin
    if reverseOutput:
        result = newMax - portion
    return int(result)


def netcheck():
    child = subprocess.Popen(['iwconfig'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=False)
    streamdata = child.communicate()[0].decode('UTF-8').split('\n')
    if child.returncode == 0:
        for each in streamdata:
            if each.find('ESSID:') != -1:
                ssid = each.split(':')[1].replace('"', '').strip()
            elif each.find('Frequency') != -1:
                apmac = each.split('Access Point: ')[1].strip()
                channel = each.split('Frequency:')[1].split(' Access Point:')[0].strip()
                if channel[0] == "5":
                    band = "A"
                elif channel[0] == "2":
                    band = "B"
                else:
                    band = ""
            elif each.find('Link Quality') != -1:
                linkqual = each.split('=')[1].split(' Signal level')[0].strip()
                signal = int(each.split('=')[2].split(' ')[0].strip())
                signal_percent = remap(signal, -80, -35, 0, 100)
                if signal_percent > 100:
                    signal_percent = 100
            elif each.find('Bit Rate') != -1:
                bitrate = each.split('=')[1].split('Tx-Power')[0].strip()
                bitrate = bitrate.split(' Mb/s')[0]
                bitrate = int(float(bitrate))
                bitrate = str(bitrate) + ' Mb/s'

        if connect():
            internet = "True"
        else:
            internet = "False"
        try:
            inet_file = open(str(net_file), 'w')
            inet_file.write(f'internet={internet}\nssid={ssid}\napmac={apmac}\nband={band}\nchannel={channel}\ndbm={signal}\nsignal_percent={signal_percent}\nquality={linkqual}\nbitrate={bitrate}\n')
            inet_file.close()
        except:
            net_file.touch()


while True:
    netcheck()
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
        if ctz != ntz and ntz is not None:
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
