#!/usr/bin/env python

###########################################################
# Script: vos_get_service.py
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


print sys.argv[1]


requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

api_get_serv = "/vos-api/configure/v1/services/" + sys.argv[1]

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}


vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')

vos_session.post(api_proto+'://'+hostname, verify=False)

vos_serv_req = vos_session.get(api_proto+'://'+hostname+api_get_serv,headers=api_header_all,verify=False)

# Need to add a check here.
#if vos_dest_req.status_code !=200:
#    print vos_dest_req.status_code


pprint(vos_serv_req.text)