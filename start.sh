#!/bin/sh

## Put your options here - the service unit will run this script, so that
## you don't need to 'daemon-reload' every time you want to change settings.
##
## It's a good idea to allow only root to write to this file: 
##
## sudo chown root:root start.sh; sudo chmod 700 start.sh
##

#VENV="/home/pi/.virtualenvs/papertty/bin/python3"
#${VENV} papertty.py --driver epd2in13 terminal --autofit

#./papertty.py --driver it8951 terminal --cols 66 --rows 31 --noclear --font ../AndaleMo.TTF --size 20 --portrait
#./papertty.py --driver it8951 terminal --cols 72 --rows 27 --noclear --font ../ter-u22b_unicode.pil --portrait --sleep 0.3
./papertty.py --driver it8951 terminal --cols 66 --rows 31 --noclear --font ../AndaleMo.TTF --size 20 --portrait
#./papertty.py --driver it8951 terminal --cols 66 --rows 28 --noclear --font ../Consolas/consola.ttf --size 22 --portrait --sleep 0.3 --spacing 4
