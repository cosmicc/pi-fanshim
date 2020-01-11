#!/usr/bin/env python3
import sys


def freq_breakdown(freq):
    if freq <= 30:
        itu_abbr = 'ELF'
        itu_num = 1
        band_desc = 'Extremely Low Frequency'
    elif freq <= 300:
        itu_abbr = 'SLF'
        itu_num = 2
        band_desc = 'Super Low Frequency'
    elif freq <= 3000:
        itu_abbr = 'ULF'
        itu_num = 3
        band_desc = 'Ultra Low Frequency'
    elif freq <= 30000:
        itu_abbr = 'VLF'
        itu_num = 4
        band_desc = 'Very Low Frequency'

    elif freq <= 300000:
        itu_abbr = 'LF'
        itu_num = 5
        band_desc = 'Low Frequency'
        if freq >= 135700 and freq <= 1378:
            meters = '2200m'
            bandtype = 'Amateur'

    elif freq <= 3000000:
        itu_abbr = 'MF'
        itu_num = 6
        band_desc = 'Medium Frequency'
        if freq >= 472000 and freq <= 4790:
            meters = '630m'
            bandtype = 'Amateur'
        elif freq >= 1800000 and freq <= 2000000:
            meters = '160m'
            bandtype = 'Amateur'

    elif freq <= 30000000:
        itu_abbr = 'HF'
        itu_num = 7
        ieee = 'HF'
        band_desc = 'High Frequency'
        if freq >= 3500000 and freq <= 4000000:
            meters = '80m'
            bandtype = 'Amateur'
        elif freq >= 5330500 and freq <= 5405000:
            meters = '60m'
            bandtype = 'Amateur'
        elif freq >= 7000000 and freq <= 7300000:
            meters = '40m'
            bandtype = 'Amateur'
        elif freq >= 10100000 and freq <= 10150000:
            meters = '30m'
            bandtype = 'Amateur'
        elif freq >= 14000000 and freq <= 14350000:
            meters = '20m'
            bandtype = 'Amateur'
        elif freq >= 18068000 and freq <= 18168000:
            meters = '17m'
            bandtype = 'Amateur'
        elif freq >= 21000000 and freq <= 21450000:
            meters = '15m'
            bandtype = 'Amateur'
        elif freq >= 24890000 and freq <= 24990000:
            meters = '12m'
            bandtype = 'Amateur'
        elif freq >= 28000000 and freq <= 29700000:
            meters = '10m'
            bandtype = 'Amateur'

    elif freq <= 300000000:
        itu_abbr = 'VHF'
        itu_num = 8
        ieee = 'VHF'
        band_desc = 'Very High Frequency'
        if freq >= 50000000 and freq <= 54000000:
            meters = '6m'
            bandtype = 'Amateur'
        elif freq >= 144100000 and freq <= 148000000:
            meters = '2m'
            bandtype = 'Amateur'
        elif freq >= 219000000 and freq <= 225000000:
            meters = '1.25m'
            bandtype = 'Amateur'

    elif freq <= 3000000000:
        itu_abbr = 'UHF'
        itu_num = 9
        band_desc = 'Ultra High Frequency'
        if freq >= 420000000 and freq <= 450000000:
            meters = '70cm'
            bandtype = 'Amateur'
        elif freq >= 902000000 and freq <= 928000000:
            meters = '33cm'
            bandtype = 'Amateur'
        elif freq >= 1240000000 and freq <= 1300000000:
            meters = '23cm'
            bandtype = 'Amateur'

    elif freq <= 30000000000:
        itu_abbr = 'SHF'
        itu_num = 10
        band_desc = 'Super High Frequency'

    elif freq <= 300000000000:
        itu_abbr = 'EHF'
        itu_num = 11
        band_desc = 'Extremely High Frequency'

    elif freq <= 3000000000000:
        itu_abbr = 'THF'
        itu_num = 12
        band_desc = 'Terahertz Frequency'

    if freq <= 250000000:
        nato = 'A'
    elif freq <= 500000000:
        nato = 'B'
    elif freq <= 1000000000:
        nato = 'C'
    elif freq <= 2000000000:
        nato = 'D'
    elif freq <= 3000000000:
        nato = 'E'
    elif freq <= 4000000000:
        nato = 'F'
    elif freq <= 6000000000:
        nato = 'G'
    elif freq <= 8000000000:
        nato = 'H'
    elif freq <= 10000000000:
        nato = 'I'
    elif freq <= 20000000000:
        nato = 'J'
    elif freq <= 40000000000:
        nato = 'K'
    elif freq <= 60000000000:
        nato = 'L'
    elif freq <= 100000000000:
        nato = 'M'

    if freq >= 148500 and freq <= 283500:
        broadcast = 'Longwave AM'
    elif freq >= 525000 and freq <= 1710000:
        broadcast = 'Mediumwave AM'
    if freq >= 3000000 and freq <= 30000000:
        broadcast = 'Shortwave AM'
    elif freq >= 47000000 and freq <= 68000000:
        broadcast = 'VHF TV'
    elif freq >= 87500000 and freq <= 108000000:
        broadcast = 'FM Radio'
    elif freq >= 470000000 and freq <= 582000000:
        broadcast = 'UHF TV'
    elif freq >= 582000000 and freq <= 862000000:
        broadcast = 'UHF TV'

    if freq > 300000000 and freq <= 1000000000:
        ieee = 'UHF'
    elif freq > 1000000000 and freq <= 2000000000:
        ieee = 'L'
    elif freq > 2000000000 and freq <= 4000000000:
        ieee = 'S'
    elif freq > 4000000000 and freq <= 8000000000:
        ieee = 'C'
    elif freq > 8000000000 and freq <= 12000000000:
        ieee = 'X'
    elif freq > 12000000000 and freq <= 18000000000:
        ieee = 'Ku'
    elif freq > 1800000000 and freq <= 27000000000:
        ieee = 'K'
    elif freq > 27000000000 and freq <= 40000000000:
        ieee = 'Ka'
    elif freq > 40000000000 and freq <= 75000000000:
        ieee = 'V'
    elif freq > 75000000000 and freq <= 110000000000:
        ieee = 'W'
    elif freq > 110000000000 and freq <= 300000000000:
        ieee = 'mm'

    if freq >= 118000000 and freq <= 137000000:
        bandtype = 'Air Band'
    elif freq >= 155500000 and freq <= 174000000:
        bandtype = "Marine VHF"
    elif freq >= 26965000 and freq <= 27405000:
        bandtype = "CB"
    elif freq >= 462562500 and freq <= 467725000:
        bandtype = "GMRS"

    return {'band_desc': band_desc, 'band_type': bandtype, 'meters': meters, 'itu_abbr': itu_abbr, 'itu_num': itu_num, 'ieee': ieee, 'nato': nato, 'broadcast': broadcast}


if __name__ == '__main__':
    if sys.argv[0]:
        freq_breakdown()
    else:
        print('You need to specify a frequency. eg: 123.000.000')
        exit(1)