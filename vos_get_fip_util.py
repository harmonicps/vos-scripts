#!/usr/bin/env python

###########################################################
# Script: vos_get_fip_util.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC. 
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 05/16/2017
# Version 1.0
###########################################################

# vos.py needs to be in the same path as this script.
import vos

cl_list = '''
10.105.154.31
10.105.154.11
10.105.154.32
10.105.154.12
10.105.154.33
10.105.154.13
10.105.154.34
10.105.154.14
10.105.154.35
10.105.154.15
10.105.154.36
10.105.154.16
10.105.154.37
10.105.154.17
10.105.154.38
10.105.154.18
10.105.154.39
10.105.154.19
10.105.154.40
10.105.154.20
10.105.154.41
10.105.154.21
10.105.154.42
10.105.154.22
10.105.154.43
10.105.154.23
10.105.154.44
10.105.154.24
10.105.154.45
10.105.154.25
10.105.154.46
10.105.154.26
10.105.154.47
10.105.154.27
10.105.154.48
10.105.154.28
'''

session = vos.vos_get_session("vos","vossdk")

cliplist = cl_list.split("\n")

fip_list = []

for clip in cliplist:

    if clip:
        cl_fips = vos.get_fip_ip(session,clip)
        for fip in cl_fips:
            if not fip in fip_list:
                fip_list.append(fip)


for fips in fip_list:
    print fips


