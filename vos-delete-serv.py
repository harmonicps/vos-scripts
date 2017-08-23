#!/usr/bin/env python

###########################################################
# Script: vos_delete_serv.py
# Author: John Vasconcelos
# Date: 04/20/2017
# Version 1.1
###########################################################

from pprint import pprint
import requests
import json
import sys


if not len(sys.argv) ==  2:
    print "Enter the Service ID !!!!!!"
    sys.exit(2)


requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

service_id = sys.argv[1]

api_del_serv = "/vos-api/configure/v1/services/" + service_id

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}


vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')

vos_session.post(api_proto+'://'+hostname, verify=False)

print "Deleting Service URL: " + api_proto + "://" + hostname + api_del_serv + "\n\n\n"
vos_serv_req = vos_session.delete(api_proto+'://'+hostname+api_del_serv,headers=api_header_all,verify=False)

# Need to add a check here.
#if vos_dest_req.status_code !=200:
#    print vos_dest_req.status_code

print vos_serv_req.text
