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
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


vos_session = vos.vos_get_session()

cl_session = vos.vos_get_session("vos","vossdk")

vosrt = raw_input("Enter the VOS RT Url:\n")



args = sys.argv[1]



cl_list = vos.vos_get_cl_list(vosrt,vos_session)


for cl in cl_list:
    
    if args == "status":

        api_header = {'user-agent':'Accept: */*'}

        uri = 'https://'+cl['clip']+"/vos-api/upgrade/v1/runtime/upgrade"

        ret = cl_session.get(uri,headers=api_header,verify=False)

        print "CL: %s - IP: %s Upgrade State: %s" %(cl['clname'],cl['clip'],ret.json()['upgradeState'])

    else:

        print "Upgrading CL %s IP: %s with Bundle %s..." %(cl['clname'],cl['clip'],args)

        api_header = {'Content-Type':'application/json' , 'Accept':'*/*'}

        uri = 'https://'+cl['clip']+"/vos-api/upgrade/v1/runtime/upgrade"

        param = {"targetVersion": args}

        ret = cl_session.post(uri,headers=api_header,data=param,verify=False)

        print ret

