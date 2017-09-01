#!/usr/bin/env python


###########################################################
# Script: vos_serv_restart.py
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

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--batch_file', dest='batch_file', action='store', help='Batch File with services to be processed.', required=True)
    parser.add_argument('--service_off', dest='service_off', action='store_true', help='Off line Service. Provide Service ID or Name', required=False)
    parser.add_argument('--service_on', dest='service_on', action='store_true', help='On line Service. Provide Service ID or Name', required=False)
    parser.add_argument('--upgrade', dest='service_upgrade', action='store_true', help='Set the Upgrade Flag to On', required=False)

    args = parser.parse_args()

    if args.service_off and args.service_on:
        print "Pick either --service_off or --service_on option."
        sys.exit(2)

    if not os.path.isfile(args.batch_file):
        print "File %s does not exist !!" %args.batch_file
        sys.exit(2)
    
    vosrt = raw_input("Enter the VOS RT Address:\n")
    
    vos_session = vos.vos_get_session()

    proto = "https"

    f = open(args.batch_file)

    for item in f:

        servn = item.strip()

        if args.service_off:
            print vos.vos_service_offline(servn,vosrt,vos_session)
        if args.service_on:
            if args.service_upgrade:
                print vos.vos_service_online(servn,vosrt,vos_session,proto,True)
            else:
                print vos.vos_service_online(servn,vosrt,vos_session,proto)


if __name__ == "__main__":
    main(sys.argv[1:])
