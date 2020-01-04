#!/bin/env python3

import subprocess


scale = 16
num_of_bits = 19

result = subprocess.run(['vcgencmd', 'get_throttled'], stdout=subprocess.PIPE)
res = result.stdout.decode()
hexval = res.split('=')[1]

hexval = "0x50005"

b = bin(int(hexval, scale))[2:].zfill(num_of_bits)

if b[0] == '1':
    throttle_hist = True
else:
    throttle_hist = False
if b[1] == '1':
    cap_hist = True
else:
    cap_hist = False
if b[2] == '1':
    undervolt_hist = True
else:
    undervolt_hist = False

if b[17] == '1':
    throttle_now = True
else:
    throttle_now = False
if b[18] == '1':
    cap_now = True
else:
    cap_now = False
if b[19] == '1':
    undervolt_now = True
else:
    undervolt_now = False

print(throttle_now, throttle_hist, cap_now, cap_hist, undervolt_now, undervolt_hist)