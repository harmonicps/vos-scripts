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
import getpass
import yaml

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--batch_file', dest='batch_file', action='store', help='Batch File with services to be processed.', required=True)
    parser.add_argument('--image_id', dest='image_id', action='store', help='Slate Image ID to be set on services', required=False)
    parser.add_argument('--new-profile', dest='prof_id', action='store', help='New Profile ID', required=False)



    args = parser.parse_args()

    vosrt = args.cloud_url

    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username

    passwd = getpass.getpass("Enter the Password:\n")

    vos_session = vos.vos_get_session(user,passwd)

    servs = vos.vos_get_service_all(vosrt,vos_session)

    srv_yaml = yaml.safe_load(servs.text)

    if not os.path.isfile(args.batch_file):
        print "File %s does not exist !!" %args.batch_file
        sys.exit(2)

    f = open(args.batch_file)

    for serv in srv_yaml:

        for item in f:

            if serv['name'] == item.strip():

                if args.image_id:
                    if not serv['addons']:
                        serv['addons'] = {"logoAddon": None,"graphicsAddon": None,"videoInsertionAddon": None,"trafficAddon": None,"casAddon": None,
                                          "drmAddon": None,"scte35SlateAddon": {"imageId": args.image_id}}

                    else:
                        serv['addons']['scte35SlateAddon'] = {"imageId": args.image_id}

                if args.prof_id:
                    serv['profileId'] = args.prof_id


                param = json.dumps(serv)

                print "Creating service %s" %serv['name']
                print param
                print vos.vos_mod_service(serv['id'],param,vosrt,vos_session)
                time.sleep(5)

        f.seek(0)

if __name__ == "__main__":
    main(sys.argv[1:])
