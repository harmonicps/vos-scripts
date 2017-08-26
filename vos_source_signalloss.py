#!/usr/bin/env python
###########################################################
# Script: vos_source_signallosspy
# NOTE: THIS SCRIPT IS NOT SUPPORTED OR TESTED BY HARMONIC.
#       USE IT AT YOUR OWN RISK !!!!
# Author: Satish Botla
# Script to add SIGNAL_LOSS imageId to input slateSettings
# Input: sources.txt
# List of the sources names 
# Date: 06/05/2017
# Version 1.1
###########################################################
# vos.py needs to be in the same path as this script.
import vos
import sys
import argparse
import os
import getpass
import yaml, json
import uuid
import time
from pprint import pprint
import requests

vos_session = vos.vos_get_session()
vosrt = "10.105.163.3"
slate_img = "c2c58142-ffca-19c1-2b7f-79ac484fd360"
f = open('sources.txt', 'r')
content = f.readlines()
content = [x.strip() for x in content]
for sourcename in content:
    print(sourcename)
    # Function to get json data of a source provided by the sources.txt
    srcs = vos.vos_get_source_name(sourcename,vosrt,vos_session)
    sr_opt = yaml.safe_load(srcs.text)
    print(sr_opt)
    print sr_opt[0]['id']
    print "\n"
    # Check if the slateSettings or present or not
    if not sr_opt[0]['inputs'][1]['slateSettings']:
        sr_opt[0]['inputs'][1]['slateSettings'] = {"type": "SIGNAL_LOSS","imageId": "c2c58142-ffca-19c1-2b7f-79ac484fd360","customSlateSettings": None}
    
    # Check if the slateSettings has correct imageId
    elif not sr_opt[0]['inputs'][1]['slateSettings']['imageId'] == "c2c58142-ffca-19c1-2b7f-79ac484fd360":
        sr_opt[0]['inputs'][1]['slateSettings']['imageId'] = "c2c58142-ffca-19c1-2b7f-79ac484fd360"

    # Check to stop duplication of adding same imageId
    elif(sr_opt[0]['inputs'][1]['slateSettings']['imageId'] == "c2c58142-ffca-19c1-2b7f-79ac484fd360"):
        print("Already atatched SIGNAL LOSS imageId")
        continue

    param = json.dumps(sr_opt[0])
    print param
     
    # Function making a put request to configure source with the added input slateSettings ImageID
    print vos.vos_mod_source(sr_opt[0]['id'],param,vosrt,vos_session)

    time.sleep(20)

