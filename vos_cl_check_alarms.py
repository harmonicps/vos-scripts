#!/usr/bin/env python

###########################################################
# Script: vos_cl_check_alarms.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 08/25/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.

import vos
import sys
import argparse
import getpass
import time


def get_notifications(cl_ip,vos_session,cl_session,nt_state,result_count):

            cl_notif = vos.vos_get_notifications(nt_state,result_count,cl_ip,vos_session)
            
            if cl_notif:
                if cl_notif.status_code == 403:
                    print "CL %s Login Failed. Trying with Legacy Password." %cl_ip
                    cl_notif = vos.vos_get_notifications(nt_state,result_count,cl_ip,cl_session)
    
                if cl_notif.status_code == 200:
                    for notif in cl_notif.json():
    
                        time_assert = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(notif['creationTime'] / 1000))
    
                        time_resolv = ""
    
                        if notif['resolvedTime']:
                            time_resolv = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(notif['resolvedTime'] / 1000))
                        
                        print '%-18s %-12s %-10s %-22s %-22s %-40s %-40s %s' %(cl_ip , notif['severity'] , notif['state'] , time_assert , time_resolv , notif['title'] , notif['channelName'] , notif['objectName'])


def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Check Notifications***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --active --cl-ip=10.105.134.5', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--cl_file', dest='cl_file', action='store', help='Source to CL Association File', required=False)
    parser.add_argument('--cl_ip', dest='cl_ip', action='store', default='', help='Cloudlink IP', required=False)
    parser.add_argument('--result_count', dest='result_count', action='store', default=20, help='Amount of Notifications. Default is 20.', required=False)
    parser.add_argument('--all_notif', dest='all_notif', action='store_true', help='Shows all Notifications', required=False)


    args = parser.parse_args()
   
    if not args.cloud_username:
        user = raw_input("Enter the Username for VOS:\n")
    else:
        user = args.cloud_username
   
    vosrt = args.cloud_url

    passwd = getpass.getpass("Enter the Password:\n")

    vos_session = vos.vos_get_session(user,passwd)
    
    cl_session = vos.vos_get_session("vos","vossdk")


    nt_state = ""

    if not args.all_notif:
        nt_state = "ACTIVE"


    print '%-18s %-12s %-10s %-22s %-22s %-40s %-40s %s' %("CL" , "SEVERITY" , "STATE" , "TIME ASSERT" , "TIME RESOLVE" , "ALARM" , "SERVICE" , "OBJECT NAME")

    if not args.cl_ip:

        cl_list = vos.vos_get_cl_list(vosrt,vos_session)

        for cl in cl_list:

            get_notifications(cl['clip'],vos_session,cl_session,nt_state,args.result_count)

    else:
        
        get_notifications(args.cl_ip,vos_session,cl_session,nt_state,args.result_count)


if __name__ == "__main__":
    main(sys.argv[1:])
