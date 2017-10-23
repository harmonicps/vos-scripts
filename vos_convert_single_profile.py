#!/usr/bin/env python


###########################################################
# Script: vos_convert_single_profile.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 10/02/2017
# Version 1.1
###########################################################

'''Example command:
./vos_migrate_services.py --rt_from vosdashboard.dfwcpcpurple.pod1.ds.dtvops.net --rt_to vosdashboard.dfwcpcpurple.pod3.ds.dtvops.net
 --serv_file serv-f.txt --src_file src-f.txt --ats_file dest-f.txt --blackout_img http://myblackoutimage.com/img.png --sigloss_img http://signalossimage.com/img.png

'''

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import json
import vos
import time
import getpass
import yaml
import uuid
import datetime


#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-migration-' + now.strftime("%Y-%m-%d-%H%M") + '.log'

#Convert Configuration to Single Profile
def convert_single_prof(srv_file,sp_file,vosrt,vos_session):
    
    sp_trans = {}
    sp_origin = {}

    for sp in sp_file:
        spl = sp.strip().split(',')
        if "origin" in spl[0]:
            if "gmott" in spl[0]:
                sp_origin['gmott'] = spl[1]
            else:
                sp_origin['dfw'] = spl[1]
        else:
            if "480" in spl[0]:
                sp_trans['480'] = spl[1]
            elif "720" in spl[0]:      
                sp_trans['720'] = spl[1]
            elif "1080" in spl[0]:      
                sp_trans['1080'] = spl[1]

    print sp_trans

    print sp_origin

    for srv in srv_file:
        srv_name = srv.strip()
        srv_namesp = srv_name.split('.')
        srv_namesp.pop()
        srv_namesp = (".").join(srv_namesp)

        vos_serv = vos.vos_get_service_name(srv_name,vosrt,vos_session)

        if vos_serv.status_code == 200:

            serv_yaml = yaml.safe_load(vos_serv.text)

            serv_yaml[0]['name'] = srv_namesp

            if "480" in srv_namesp:
                serv_yaml[0]['profileId'] = sp_trans['480']
            elif "720" in srv_namesp:
                serv_yaml[0]['profileId'] = sp_trans['720']
            elif "1080" in srv_namesp:
                serv_yaml[0]['profileId'] = sp_trans['1080']
            else:
                vos.log_write("ERROR","No Transcode Profile for Service %s Skipping service" %srv_name,log_file)
                continue

            param = json.dumps(serv_yaml[0])

            vos_ret = vos.vos_mod_service(serv_yaml[0]['id'],param,vosrt,vos_session)

            if vos_ret.status_code == 200:
                vos.log_write("INFO","Service %s has been changed to %s" %(srv_name,vos_ret.json()['name']),log_file)
                vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
            else:
                vos.log_write("ERROR","Failed to Modify Service %s !!!! Fix Issue and Rerun Script." %srv_name,log_file)
                vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
                vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
                sys.exit(2)