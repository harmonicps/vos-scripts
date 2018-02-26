#!/usr/bin/env python


###########################################################
# Script: vos_source_disable_audio.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 02/02/2018
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import getpass
import yaml, json
import time

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Source Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --export --file=sources.txt', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--file', dest='src_file', action='store', help='Batch File with services to be processed.', required=True)
    parser.add_argument('--dryrun', dest='dryrun', action='store_true', help='Set Other Misc. Options', required=False)

    args = parser.parse_args()

    if args.dryrun:
        print "Script is running as Dryrun no changes will be applied !!"

    user = raw_input("Enter the Username for VOS:\n")

    passwd = getpass.getpass("Enter the Password:\n")

    vos_session = vos.vos_get_session(user,passwd)

    vosrt = args.cloud_url

    if not os.path.isfile(args.src_file):
        print "File %s does not exist !!" %args.src_file
        sys.exit(2)

    f = open(args.src_file)


    srcount = 0
    ret = []

    for item in f:
        srcname = item.strip()
        srcs = vos.vos_get_source_name(srcname,vosrt,vos_session)
        srcsy = yaml.safe_load(srcs.text)
        srcsy = srcsy[0]

        if srcsy['inputs'][0]['zixiSettings']['grooming']:
            if len(srcsy['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks']) > 1:
                if not srcsy['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][1]['skipProcessing']:
                    srcsy['inputs'][0]['zixiSettings']['grooming']['audioGrooming']['tracks'][1]['skipProcessing'] = True

                    param = json.dumps(srcsy)

                    if args.dryrun:
                        print "\nDry Run on Service %s - Below Parameters would be applied if not in Dryrun Mode.\n" %srcsy['name']
                        print param
                        ret.append("Script would disable 2nd Audio for Source %s" %srcsy['name'])
                    else:
                        print "\nDisabling 2nd Audio for Source %s\n" %srcsy['name']
                        print vos.vos_mod_source(srcsy['id'],param,vosrt,vos_session)
                        ret.append("Disabled 2nd Audio for Source %s" %srcsy['name'])

                    srcount += 1
                    time.sleep(5)
        else:
            print "Source %s is configured but not Groomed !!!" %srcsy['name']
            ret.append("Source %s is configured but not Groomed !!!" %srcsy['name'])

    for r in ret:
        print r
    print "%d Sources had the 2nd Audio Disabled" %srcount



if __name__ == "__main__":
    main(sys.argv[1:])
