#!/usr/bin/env python


###########################################################
# Script: vos_serv_delete.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import json

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--json_file', dest='json_file', action='store', help='Batch File with services to be processed.', required=False)
    parser.add_argument('--id', dest='serv_id', action='store', help='Service ID to be deleted', required=False)


    args = parser.parse_args()

    vos_session = vos.vos_get_session()

    vosrt = args.cloud_url
  
    
    if args.json_file:
        if not os.path.isfile(args.json_file):
            print "File %s does not exist !!" %args.json_file
            sys.exit(2)


        f = open(args.json_file)

        serv_json = json.load(f)

        for serv in serv_json:
            
            print "Deleting Service: %s" %serv['name']

            print vos.vos_service_delete(serv['id'],vosrt,vos_session)


    if args.serv_id:
        print "Not implemented yet !!!"

if __name__ == "__main__":
    main(sys.argv[1:])
