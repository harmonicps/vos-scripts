#!/usr/bin/env python


###########################################################
# Script: vos_delete_config.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 10/26/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import json
import datetime
import time

#Logfile Name Construction
now = datetime.datetime.now()
log_file = 'vos-delete-config-' + now.strftime("%Y-%m-%d-%H%M") + '.log'

def continue_check(op,vosrt):

    ret = False

    while True:

        m_continue = raw_input("ARE YOU SURE YOU WANT TO DELETE %s from RT: %s? (Y/N) : " %(op,vosrt))

        if m_continue.lower() not in ('y' , 'n'):
            print "Answer not valid. Please enter Y or N !"
            continue
        else:
            break

    if m_continue.lower() == "n":
        print "Script has been Aborted"
        sys.exit(2)
    else:
        ret = True



    m_continue = raw_input("ARE YOU REALLY SURE YOU WANT TO DELETE %s from RT: %s? Type 'DELETE': " %(op,vosrt))

    if not m_continue == "DELETE":
        print "Script has been Aborted"
        sys.exit(2)
    else:
        ret = True

    return ret




def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--service', dest='service', action='store_true', help='Delete Service', required=False)
    parser.add_argument('--destination', dest='destination', action='store_true', help='Delete Destination', required=False)
    parser.add_argument('--source', dest='source', action='store_true', help='Delete Source', required=False)
    parser.add_argument('--all', dest='all', action='store_true', help='Delete All', required=False)
    parser.add_argument('--id', dest='id', action='store', help='Delete by ID', required=False)


    args = parser.parse_args()


    if not args.service and not args.source and not args.destination:
        print "Please enter an option for Deletion. --service or --destination or --source"
        sys.exit(2)

    if not args.all and not args.id:
        print "You need to specify either --all or --id option"
        sys.exit(2)

    if args.all and args.id:
        print "You need to specify either --all or --id option"
        sys.exit(2)

    vos_session = vos.vos_get_session()

    vosrt = args.cloud_url


    # Delete Services
    if args.service:

        if args.source or args.destination:
            print "You can only pick one Option for Deletion ! Pick either --source or --service or --destination"
            sys.exit(2)

        #Delete all Services on RT
        if args.all:

            if not continue_check("ALL SERVICES",vosrt):
                sys.exit(2)

            servs = vos.vos_get_service_all(vosrt,vos_session)

            for serv in servs.json():


                vos.log_write("INFO","Deleting Service %s ID: %s" %(serv['name'],serv['id']),log_file)

                vos_ret = vos.vos_service_delete(serv['id'],vosrt,vos_session)

                if vos_ret.status_code == 200:

                    vos.log_write("INFO","\n%s" %json.dumps(serv),log_file)
                    time.sleep(4)
                else:
                    vos.log_write("ERROR","Failed to Delete Service %s. Error: %s - %s " %(serv['name'],vos_ret,vos_ret.text),log_file)


    # Delete Destinations
    if args.destination:

        if args.source or args.service:
            print "You can only pick one Option for Deletion ! Pick either --source or --service or --destination"
            sys.exit(2)

        #Delete all Destinations on RT
        if args.all:

            if not continue_check("ALL DESTINATIONS",vosrt):
                sys.exit(2)

            dests = vos.vos_get_destination_all(vosrt,vos_session)

            for dest in dests.json():


                vos.log_write("INFO","Deleting Destination %s ID: %s" %(dest['name'],dest['id']),log_file)

                vos_ret = vos.vos_destination_delete(dest['id'],vosrt,vos_session)

                if vos_ret.status_code == 200:

                    vos.log_write("INFO","\n%s" %json.dumps(dest),log_file)
                    time.sleep(4)
                else:
                    vos.log_write("ERROR","Failed to Delete Destination %s. Error: %s - %s " %(dest['name'],vos_ret,vos_ret.text),log_file)

    # Delete Sources
    if args.source:

        if args.destination or args.service:
            print "You can only pick one Option for Deletion ! Pick either --source or --service or --destination"
            sys.exit(2)

        #Delete all Sources on RT
        if args.all:

            if not continue_check("ALL SOURCES",vosrt):
                sys.exit(2)

            srcs = vos.vos_get_source_all(vosrt,vos_session)

            for src in srcs.json():


                vos.log_write("INFO","Deleting Source %s ID: %s" %(src['name'],src['id']),log_file)

                vos_ret = vos.vos_source_delete(src['id'],vosrt,vos_session)

                if vos_ret.status_code == 200:

                    vos.log_write("INFO","\n%s" %json.dumps(src),log_file)
                    time.sleep(4)
                else:
                    vos.log_write("ERROR","Failed to Delete Source %s. Error: %s - %s " %(src['name'],vos_ret,vos_ret.text),log_file)



if __name__ == "__main__":
    main(sys.argv[1:])
