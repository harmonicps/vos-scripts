#!/usr/bin/env python

"""
###########################################################
# Script: vos_dest_prof_change.py
# Author: John Vasconcelos
# Date: 08/31/2017
# Version 2.1
###########################################################
"""

# vos.py needs to be in the same path as this script.
import vos
import requests
import argparse
import json,yaml
import time
import sys
import os
import getpass


def change_prof(vosrt,did,newprof,session):

    dest_req = vos.vos_get_dest_id(did,vosrt,session)

    dest_mod = yaml.safe_load(dest_req.text)

    print "Changing Dest %s - Profile %s with new Profile %s" %(dest_mod['name'], dest_mod['destinationProfileId'] , newprof)

    dest_mod['destinationProfileId'] = newprof
    print dest_mod['destinationProfileId']
    
    param = json.dumps(dest_mod)
 
    ret = vos.vos_mod_dest(did,param,vosrt,session)
    
    print ret

    time.sleep(30) # Wait n number of seconds in between API Calls.



def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Check Notifications***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --batch_file=dest.txt --new_prof_id=f024bea3-cc44-8e19-dbcc-fc3a20dfdcde', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--batch_file', dest='batch_file', action='store', help='Batch File with Destination Names to be Processed', required=True)
    parser.add_argument('--new_prof_id', dest='new_prof_id', action='store', default='', help='Destination Profile ID to be changed to.', required=True)


    args = parser.parse_args()

    if not os.path.isfile(args.batch_file):
        print "File %s does not exist !!" %args.batch_file
        sys.exit(2)

    dest_file = open(args.batch_file)

    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username
   
    vosrt = args.cloud_url

    passwd = getpass.getpass("Enter the Password:\n")

    vos_session = vos.vos_get_session(user,passwd)

    vosrt = args.cloud_url       

    vos_dest_req = vos.vos_get_dest_all(vosrt,vos_session).json()

    for ditem in vos_dest_req:
    
        d_id = ditem['id']
    
        d_name = ditem['name']
        
        for dest in dest_file:

            dest_name = dest.strip()

            if dest_name == d_name:

                d_prof = ditem['destinationProfileId']
    
                if d_prof != args.new_prof_id: 
    
                    change_prof(vosrt,d_id,args.new_prof_id,vos_session)

        dest_file.seek(0) # goes back to the begining of the file.
    

if __name__ == "__main__":
    main(sys.argv[1:])
    
