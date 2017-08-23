#!/usr/bin/env python


###########################################################
# Script: vos_serv_helper.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
#import vos
import sys
import argparse
import os
import json
import vos
import time

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--image_id', dest='image_id', action='store', help='Slate Image ID to be set on services', required=True)


    args = parser.parse_args()

    #vos_session = vos.vos_get_session("dfw.ote@gmail.com","dfwote*1")

    vosrt = args.cloud_url

    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username

    #passwd = getpass.getpass("Enter the Password:\n")

    passwd = "dfwote*1"

    slate_img = args.image_id

    vos_session = vos.vos_get_session(user,passwd)

    servs = vos.vos_get_service_all(vosrt,vos_session)

    srv_yaml = yaml.safe_load(servs.text)

    for serv in srv_yaml[0]:

        if not serv['addons']:
            serv['addons'] = {"logoAddon": None,"graphicsAddon": None,"videoInsertionAddon": None,"trafficAddon": None,"casAddon": None,
                              "drmAddon": None,"scte35SlateAddon": {"imageId": slate_img}}
       
        else:
            serv['addons']['scte35SlateAddon'] = {"imageId": slate_img}
        
        param = json.dumps(serv)

        print "Creating service %s" %serv['name']
        print param
        #print vos.vos_mod_service(serv['id'],param,vosrt,vos_session)
        time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1:])
