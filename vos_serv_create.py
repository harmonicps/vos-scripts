#!/usr/bin/env python


###########################################################
# Script: vos_serv_create.py
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
    parser.add_argument('--json_file', dest='json_file', action='store', help='Batch File with services to be processed.', required=True)
    parser.add_argument('--serv_file', dest='serv_file', action='store', help='Service ID to be Created', required=True)

    args = parser.parse_args()

    vosrt = args.cloud_url

    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username

    passwd = getpass.getpass("Enter the Password:\n")


    vos_session = vos.vos_get_session(user,passwd)


    if not os.path.isfile(args.json_file):
        print "File %s does not exist !!" %args.json_file
        sys.exit(2)

    if not os.path.isfile(args.serv_file):
        print "File %s does not exist !!" %args.serv_file
        sys.exit(2)


    sjf = open(args.json_file)

    sf = open(args.serv_file)

    serv_json = json.load(sjf)

    for sv in sf:

        for serv in serv_json:
        #print serv['name']

            if serv['name'] == sv.strip():
                if len(serv['serviceSources']) ==2:
                    print "Deleting: "
                    print serv['serviceSources'][1]
                    serv['serviceSources'].pop()

                if not serv['addons']:
                    serv['addons'] = {"logoAddon": None,"graphicsAddon": None,"videoInsertionAddon": None,"trafficAddon": None,"casAddon": None,
                                      "drmAddon": None,"scte35SlateAddon": {"imageId": "d1cd154e-7b5b-24d3-a58f-29555fb83aa3"}}
                
                else:
                    serv['addons']['scte35SlateAddon'] = {"imageId": "d1cd154e-7b5b-24d3-a58f-29555fb83aa3"}
                
                param = json.dumps(serv)

                print "Creating service %s" %serv['name']
                print vos.vos_service_add(param,vosrt,vos_session)
                time.sleep(5)


if __name__ == "__main__":
    main(sys.argv[1:])
