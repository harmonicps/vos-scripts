#!/usr/bin/env python

###########################################################
# Script: vos_dest_prof_attach_cl.py
# Author: John Vasconcelos
# Date: 06/30/2017
# Version 1.1
###########################################################

import requests
import json,yaml
import time
import sys
import vos


def change_prof(did,newprof):

    api_header_put = {'Content-Type':'application/json' , 'Accept':'application/json'}

    api_dest = "/vos-api/configure/v1/destinations/" + did 

    dest_req = vos_session.get(api_proto+'://'+hostname+api_dest,headers=api_header_json,verify=False)

    dest_mod = yaml.safe_load(dest_req.text)

    print "Changing Dest %s with Profile %s with new Profile %s" %(dest_mod['name'], dest_mod['destinationProfileId'] , newprof)

    dest_mod['destinationProfileId'] = newprof
    print dest_mod['destinationProfileId']
    
    param = json.dumps(dest_mod)
 
    ret = vos_session.put(api_proto+'://'+hostname+api_dest,headers=api_header_put,data=param,verify=False)
    
    print ret

    time.sleep(120)




requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

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

vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)


d = vos_dest_req.json()

mobile_prof = "35a91a1e-d99e-49d7-0368-257b6f16ac95"

tv_prof = "f5bdfc57-a20a-9358-36e7-857a3b09cd7d"

for ditem in d:

    d_id = ditem['id']

    d_name = ditem['name']

    d_prof = ditem['destinationProfileId']

    if "mobile.origin" in d_name and d_prof != mobile_prof: 

        change_prof(d_id,mobile_prof)

    if "tv.origin" in d_name and d_prof != tv_prof:

        change_prof(d_id,tv_prof)

    
