#!/usr/bin/env python
###########################################################
# Script: vos_serv_slate_change_orange.py
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: Satish Botla
# Input: services.txt
# List of service names
# Date: 06/05/2017
# Version 1.1
###########################################################

# vos.py needs to be in the same path as this script.
#import vos
import sys
import argparse
import os
import json
import yaml
import vos
import time
import requests

# Function to get vos session
vosrt = raw_input("Enter the VOS RT Address:\n")

vos_session = vos.vos_get_session()
slate_img = "a9717984-624e-3366-293f-8c6294dbfa82"
f = open('services.txt', 'r')
content = f.readlines()
content = [x.strip() for x in content] 
for servicename in content:
    print(servicename)
    # Function to get the json of the each service decribed in the text file
    servic = vos.vos_get_service_name(servicename,vosrt,vos_session)
    serv = yaml.safe_load(servic.text)
    #print(serv)
    # Check to see the service doesn't have scte35Slateaddon, we are adding a slate imageId
    if(serv[0]['addons']['scte35SlateAddon'] == None):
        serv[0]['addons']['scte35SlateAddon'] = {"imageId": slate_img}
        param = json.dumps(serv[0])
        print "Changing slate image for Service %s" %serv[0]['name']
        print param
        print "\n"
        # Function that makes a put request to configure service with the new slate imageId
        print vos.vos_mod_service(serv[0]['id'],param,vosrt,vos_session)
        time.sleep(20)

    else:
        print("Already attached scte35SlateAddon to this service")
        time.sleep(20)














