#!/bin/bash
gcc -DNDEBUG -g -O3 -Wall -Wstrict-prototypes -fPIC -DMAJOR_VERSION=1 -DMINOR_VERSION=0 -I/usr/include -I/usr/include/python3.7 --shared pack.c -o pack.so
#gcc -I/usr/include -I/usr/include/python3.7m -fPIC -shared pack.c -o pack.o
#gcc -fPIC -I/usr/include/python3.7m -lpython3.7m --shared -o pack.so pack.c
