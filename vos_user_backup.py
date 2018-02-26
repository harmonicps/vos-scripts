#!/usr/bin/env python


###########################################################
# Script: vos_user_backup.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 10/02/2017
# Version 1.1
###########################################################

'''Example command:
./vos_migrate_services.py --rt_from vosdashboard.dfwcpcpurple.pod1.ds.dtvops.net --rt_to vosdashboard.dfwcpcpurple.pod3.ds.dtvops.net
 --serv_file serv-f.txt --src_file src-f.txt --ats_file dest-f.txt --blackout_img http://myblackoutimage.com/img.png --sigloss_img http://signalossimage.com/img.png

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


#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-user-backup-' + now.strftime("%Y-%m-%d-%H%M") + '.log'


def check_status(vos_ret,config,config_name,config_id):

    if vos_ret.status_code == 200:
        vos.log_write("INFO","%s %s ID: %s Created Successfully" %(config,config_name,config_id),log_file)
        vos.log_write("INFO","\n %s \n" %vos_ret.text,log_file)
    else:
        vos.log_write("ERROR","%s %s failed to create... ABORTING SCRIPT !!!" %(config,config_name) ,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret,log_file)
        vos.log_write("ERROR","\n %s \n" %vos_ret.text,log_file)
        sys.exit(2)


def main(argv):
    parser = argparse.ArgumentParser(description='***VOS User Backup/Restore***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='RT from where to export Configuration.', required=True)
    parser.add_argument('--user_file', dest='user_file', action='store', help='JSON File for Users', required=True)
    parser.add_argument('--backup', dest='backup', action='store_true', help='Backup Configuration', required=False)
    parser.add_argument('--restore', dest='restore', action='store_true', help='Restore Configuration', required=False)


    args = parser.parse_args()

    

    if args.backup and args.restore:
        print "Please use either --backup or --restore but not both :-)"
        sys.exit(2)


    #Creates VOS Requests Session. It will prompt for user and password.
    vos_session = vos.vos_get_session()

    vosrt = args.cloud_url

    # Backup Configuration
    if args.backup:


        #Backup Sources
        f_users = open(args.user_file,'w')

        vos_users = vos.vos_get_user_all(vosrt,vos_session)

        json.dump(vos_users.json(),f_users)

        f_users.close()

    
    #Restores Configuration
    if args.restore:


        #Checks if file exists
        if not os.path.isfile(args.user_file):
            print "File %s does not exist !!" %args.user_file
            sys.exit(2)            

      

        #Restore Users
        with open(args.user_file) as user_data:
            usr_y = yaml.safe_load(user_data)

        for usr in usr_y:

            chk_usr = vos.vos_get_user_name(usr['username'],vosrt,vos_session)

            if not chk_usr.status_code == 200:

                param = json.dumps(usr)
            
                vos_ret = vos.vos_add_user(param,vosrt,vos_session)

                check_status(vos_ret,"User",usr['name'],usr['username'])

            else:

                vos.log_write("INFO","User %s already Exists !!!" %usr['username'],log_file)



if __name__ == "__main__":
    main(sys.argv[1:])