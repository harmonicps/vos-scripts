#!/bin/python

import argparse
import sys

def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Cloud Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url=https://hkvpurple-01.nebula.video --cloud_username=USERNAME', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=False)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='vos', help='Cloudlink username', required=False)
    parser.add_argument('--mesos_url', dest='mesos_url', action='store', help='Mesos Master Url', required=False)
    parser.add_argument('--cloudlink_username', dest='cloudlink_username', action='store', default='vos', help='Cloudlink username', required=False)
    parser.add_argument('--cloudlink_password', dest='cloudlink_password', action='store', default='vossdk', help='Cloudlink password', required=False)
    parser.add_argument('--get_sysconfig', action='store_true',help='Retrieves and Prints all Services configuration in CSV', required=False)
    parser.add_argument('--get_lio_info', action='store_true',help='Retrieves and Prints all LIO Profiles', required=False)

    args = parser.parse_args()

    if args.get_sysconfig:
        print "Get Sysconfig"

    if args.get_lio_info:
        print "Get LIO Info"

if __name__ == "__main__":
    main(sys.argv[1:])