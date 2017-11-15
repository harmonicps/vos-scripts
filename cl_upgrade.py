#!/usr/bin/env python

###########################################################
# Script: cl_upgrade.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: John Vasconcelos
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
import vos
import requests
import sys
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


vosrt = raw_input("Enter the VOS RT Url:\n")
vos_session = vos.vos_get_session()

cl_manual_session = vos.vos_get_session("vos","vossdk")


args = sys.argv[1]



cl_list = vos.vos_get_cl_list(vosrt,vos_session)


for cl in cl_list:

    if args == "status":

        cl_login = "HARMONIC"

        api_header = {'user-agent':'Accept: */*'}

        uri = 'https://'+cl['clip']+"/vos-api/upgrade/v1/runtime/upgrade"

        uriinfo = 'https://'+cl['clip']+"/vos-api/system/v1/info"

        ret = vos_session.get(uri,headers=api_header,verify=False)

        if ret.status_code == 403:
            ret = cl_manual_session.get(uri,headers=api_header,verify=False)

        retinfo = vos_session.get(uriinfo,headers=api_header,verify=False)

        if retinfo.status_code == 403:
            retinfo = cl_manual_session.get(uriinfo,headers=api_header,verify=False)
            cl_login = "MANUAL"
        print "CL: %s - IP: %s Upgrade State: %s - Current Version: %s - Login is: %s" %(cl['clname'],cl['clip'],ret.json()['upgradeState'],retinfo.json()['bundleVersion'],cl_login)

    else:

        print "Upgrading CL %s IP: %s with Bundle %s..." %(cl['clname'],cl['clip'],args)

        api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

        uri = 'https://'+cl['clip']+"/vos-api/upgrade/v1/runtime/upgrade"

        param = json.dumps({"targetVersion":args})

        ret = vos_session.post(uri,headers=api_header,data=param,verify=False)

        print ret
