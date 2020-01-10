#!/usr/bin/env python3

from subprocess import PIPE, Popen, check_output, DEVNULL, run
import urllib.request
from pathlib import Path

net_file = Path('/dev/shm/network')


def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False

def remap( x, oMin, oMax, nMin, nMax ):
    #range check
    if oMin == oMax:
        print("Warning: Zero input range")
        return None

    if nMin == nMax:
        print("Warning: Zero output range")
        return None

    #check reversed input range
    reverseInput = False
    oldMin = min( oMin, oMax )
    oldMax = max( oMin, oMax )
    if not oldMin == oMin:
        reverseInput = True

    #check reversed output range
    reverseOutput = False   
    newMin = min( nMin, nMax )
    newMax = max( nMin, nMax )
    if not newMin == nMin :
        reverseOutput = True

    portion = (x-oldMin)*(newMax-newMin)/(oldMax-oldMin)
    if reverseInput:
        portion = (oldMax-x)*(newMax-newMin)/(oldMax-oldMin)

    result = portion + newMin
    if reverseOutput:
        result = newMax - portion

    return int(result)


def check():
    child = Popen(['iwconfig'], stdout=PIPE, stderr=DEVNULL, shell=False)
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
                elif channel[1] == "2":
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

check()
