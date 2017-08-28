#!/usr/bin/env python


###########################################################
# Script: vos_get_lio_serv.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 08/28/2017
# Version 1.2
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse


def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Check Notifications***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --active --cl-ip=10.105.134.5', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='RT username', required=False)
    parser.add_argument('--cloud_pass', dest='cloud_pass', action='store', default='', help='RT Password', required=False)
    parser.add_argument('--mesos_master', dest='mesos_master', action='store', default='', help='Mesos Master IP', required=False)    

    args = parser.parse_args()
    
    if args.cloud_username:
        user = args.cloud_username
    else:
        user = ""
    
    if args.cloud_pass:
        password = args.cloud_pass
    else:
        password = ""
 
    vos_session = vos.vos_get_session(user,password)
    
    if args.mesos_master:
        mesos_master = args.mesos_master
    else:
        mesos_master = raw_input("Enter the IP of the Mesos Master:\n")
    
    vosrt = args.cloud_url
    
    mtasks = vos.mesos_get_tasks(mesos_master)
    
    magents = vos.mesos_get_agents(mesos_master)
    
    lio_info = vos.vos_get_live_ingest(mtasks,magents,vosrt,vos_session)
    
    
    print "SERVICE,LIO ID,PACKAGE,NODE,NODE IP,STATE"
    
    for lio in lio_info:
        print "%s,%s,%s,%s,%s,%s" %(lio['servname'] , lio['lioid'] , lio['package'] , lio['node'] , lio['nodeip'] , lio['state'])

if __name__ == "__main__":
    main(sys.argv[1:])