#!/usr/bin/env python

###########################################################
# Script: vos_ats_prof_cl_change.py
# Author: John Vasconcelos
# Date: 06/01/2017
# Version 1.1
###########################################################

import requests
import argparse
import json,yaml
import time
import sys
import vos
import os
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def change_prof(did,clgrp,hostname,vos_session):

    api_proto = "https"

    api_header_json = {'user-agent':'Accept:application/json'}

    api_header_put = {'Content-Type':'application/json' , 'Accept':'application/json'}

    api_dest = "/vos-api/configure/v1/destinations/" + did 

    dest_req = vos_session.get(api_proto+'://'+hostname+api_dest,headers=api_header_json,verify=False)

    dest_mod = yaml.safe_load(dest_req.text)

    print "Changing Dest %s with CL GRP ID %s" %(dest_mod['name'], clgrp)

    dest_mod['outputs'][0]['ipSettings']['cloudlinkGroupId'] = clgrp
    
    param = json.dumps(dest_mod)
 
    ret = vos_session.put(api_proto+'://'+hostname+api_dest,headers=api_header_put,data=param,verify=False)
    
    print ret

    time.sleep(120)




def main(argv):
    parser = argparse.ArgumentParser(description='***VOS Source Helper***', epilog = 'Usage example:\n'+sys.argv[0]+' --cloud_url <RT URL> --export --file=sources.txt', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--cloud_url', dest='cloud_url', action='store', help='Cloud url', required=True)
    parser.add_argument('--cloud_username', dest='cloud_username', action='store', default='', help='Cloudlink username', required=False)
    parser.add_argument('--file', dest='src_file', action='store', help='Batch File with services to be processed.', required=True)

    args = parser.parse_args()
    
    api_proto = "https"
    
    hostname = args.cloud_url

    vosrt = hostname
    
    api_get_dest = "/vos-api/configure/v1/destinations"
    
    api_header_json = {'user-agent':'Accept:application/json'}
    
    api_header_all = {'user-agent':'Accept: */*'}
    
    api_header_serv_post = {'Content-Type':'application/json' , 'Accept':'*/*'}
    
    
    vos_session = requests.Session()
    vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')
    
    vos_conn_test = vos_session.post(api_proto+'://'+hostname,verify=False)
    
    if vos_conn_test.status_code != 200:
        print "Error Connecting to VOS: "
        print vos_conn_test
        sys.exit(2)
    
    if not os.path.isfile(args.src_file):
        print "File %s does not exist !!" %args.src_file
        sys.exit(2)

    f = open(args.src_file)


    vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)
    
    
    d = vos_dest_req.json()
    
    cl_list = vos.vos_get_cl_list(vosrt,vos_session)

    for dest in f:

        destname = dest.split(",")[0]
        clname = dest.split(",")[1]


        for ditem in d:
    
            d_id = ditem['id']
    
            d_name = ditem['name']
    
            if d_name == destname.strip():
            
                for cl in cl_list:
            
                    if clname.strip() == cl['clname']:
                    
                        change_prof(d_id,cl['clgroup'],hostname,vos_session)
    
    
        
if __name__ == "__main__":
    main(sys.argv[1:])