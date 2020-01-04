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


