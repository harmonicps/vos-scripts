#!/usr/bin/env python

###########################################################
# Script: vos_check.py
# Author: John Vasconcelos
# Date: 03/27/2017
# Version 1.0
###########################################################

from pprint import pprint
import requests
import json

api_proto = "https"

hostname = "10.105.152.3"

api_get_dest = "/vos-api/configure/v1/destinations"

api_get_dest_header = {'user-agent':'Accept:application/json'}


vos_session = requests.Session()
vos_session.auth = ('harmonic.dfw.prod@gmail.com','Harmonic2008!')

vos_session.post(api_proto+'://'+hostname, verify=False)


vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_get_dest_header,verify=False)

if r.status_code !=200:
    raise APIError('GET /vos-api/' {}.format(r.status_code))

for i in vos_dest_req.json():
    print vos_dest_req[i]['name']

