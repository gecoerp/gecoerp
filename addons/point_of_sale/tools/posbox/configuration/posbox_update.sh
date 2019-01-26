#!/usr/bin/env bash

sudo mount -o remount,rw /
sudo git --work-tree=/home/pi/gecoerp/ --git-dir=/home/pi/gecoerp/.git pull
sudo mount -o remount,ro /
(sleep 5 && sudo reboot) &
