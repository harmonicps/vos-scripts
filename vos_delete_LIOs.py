#!/usr/bin/env python

###########################################################
# Script: vos_delete_LIOs.py
# Author: John Vasconcelos
# Date: 06/01/2017
# Version 1.1
###########################################################

import requests
import json,yaml
import time
import sys



def vos_get_live_ingest(vosrt,session="",proto="https"):
     
    api_get_ingest_point = "/vos-api/live-ingest-origin/v1/ingest-point"
    api_header = {'user-agent':'Accept: */*'}
    uri = proto+'://'+vosrt+api_get_ingest_point

    ret = session.get(uri,headers=api_header,verify=False)

    return ret



def vos_delete_live_ingest(lioid,vosrt,session="",proto="https"):
     
    api_get_ingest_point = "/vos-api/live-ingest-origin/v1/ingest-point/"+lioid
    api_header = {'user-agent':'Accept: */*'}
    uri = proto+'://'+vosrt+api_get_ingest_point

    ret = session.delete(uri,headers=api_header,verify=False)

    return ret





requests.packages.urllib3.disable_warnings()

api_proto = "https"

vosrt = raw_input("Enter the RT Address: ")

vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')


lio_list = vos_get_live_ingest(vosrt,vos_session).json()


for lio in lio_list:

    if lio['state'] == "INITIALIZING":

        print "Deleting LIO ID: %s" %lio['id']
        print "Deleting LIO For: %s" %lio['tag']
        #print vos_delete_live_ingest(lio['id'],vosrt,vos_session)