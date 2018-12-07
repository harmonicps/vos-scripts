#!/usr/bin/env python


###########################################################
# Script: vos_drmsys_create.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 10/25/2018
# Version 1.1
###########################################################

'''Example command:
./vos_migrate_services.py --rt_from vosdashboard.dfwcpcpurple.pod1.ds.dtvops.net --rt_to vosdashboard.dfwcpcpurple.pod3.ds.dtvops.net
 --serv_file serv-f.txt --src_file src-f.txt --ats_file dest-f.txt --blackout_img http://myblackoutimage.com/img.png --sigloss_img http://signalossimage.com/img.png

###SAMPLE CSV FILE###
Name,Resource_ID,PackageType

'''

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import json
import time
import yaml
import datetime
import random


#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-backup-restore-' + now.strftime("%Y-%m-%d-%H%M") + '.log'
n_choice = '0123456789'

def checkdrm_exists(drmres,res_id):
    
    ret = False
    for item in drmres:
        if item['resourceId'] == res_id:
            ret = True

    return ret

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS DRM System Creation***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='RT from where to export Configuration.', required=False)
    parser.add_argument('--drm_sys_id', dest='drm_sys_id', action='store', help='System ID to add resoures to.', required=True)
    parser.add_argument('--drm_file', dest='drm_file', action='store', help='JSON File with DRM Resources to be created', required=True)

    args = parser.parse_args()

    #Creates VOS Requests Session. It will prompt for user and password.
    vos_session = vos.vos_get_session()

    vosrt = args.cloud_url

    
    if not os.path.isfile(args.drm_file):
        print "File %s does not exist !!" %args.batch_file
        sys.exit(2)
    

    f = open(args.drm_file)

    drm_sys = vos.vos_get_drmsys_id(args.drm_sys_id,vosrt,vos_session)

    if drm_sys.status_code==200:
        drmy = yaml.safe_load(drm_sys.text)
        resource_l = drmy['resources']
        for line in f:
            drm_data = line.strip().split(",")
            drm_id = ''.join((random.choice(n_choice)) for x in range(12))
            if not checkdrm_exists(resource_l,drm_data[1]):
                res_d = {'resourceId': drm_data[1], 'packagingType': drm_data[2], 'id': drm_id, 'name': drm_data[0]}
                resource_l.append(res_d)
            else:
                print "Resource ID %s already exists and will not be created! \n" % drm_data[1]
        drmy['resources'] = resource_l
        
        param = json.dumps(drmy)
        #Updates the DRM File.
        vos.vos_mod_drm_system(args.drm_sys_id,param,vosrt,vos_session)

    else:
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
