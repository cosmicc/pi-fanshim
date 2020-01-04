#!/bin/bash

STATUS=0x0
UNDERVOLTED=0x1

((($STATUS&UNDERVOLTED))!=0) && echo "yes" || echo "no"
