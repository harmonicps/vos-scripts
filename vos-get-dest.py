#!/usr/bin/env python

###########################################################
# Script: vos_get_dest.py
# Author: John Vasconcelos
# Date: 04/20/2017
# Version 1.1
###########################################################

from pprint import pprint
import requests
import json

requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = "vosdashboard.dfwcpcgreen.ds.dtvops.net"

api_get_dest = "/vos-api/configure/v1/destinations"

api_get_prof = "/vos-api/labwizard/v1/profiles"

api_get_cl = "/vos-api/uplink-hub/v1/uplinkGroups"

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}


vos_session = requests.Session()
vos_session.auth = ('dfw.ote@gmail.com','dfwote*1')

vos_session.post(api_proto+'://'+hostname, verify=False)

vos_prof_req = vos_session.get(api_proto+'://'+hostname+api_get_prof,headers=api_header_all,verify=False)

vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)

vos_cl_req = vos_session.get(api_proto+'://'+hostname+api_get_cl,headers=api_header_json,verify=False)

# Need to add a check here.
#if vos_dest_req.status_code !=200:
#    print vos_dest_req.status_code

d = vos_dest_req.json()

p = vos_prof_req.json()

cl = vos_cl_req.json()

#print '*'.join(("Service Name","service ID","State","Source","Source ID","Src CL","src CL ID","Src SSM","Src McIP","Src Port","Destination","Dst ID","Dst Type","Dst McIP","Dst Port","Egress CL","Egress CL ID","Dst Profile","Dst Profile ID","Prof. Version" ))


for ditem in d:
    d_id = ditem['id']
    d_name = ditem['name']
    d_type = ditem['type']
    d_profid = ditem['destinationProfileId']

    for pitem in p:
        p_id = pitem['id']
        if p_id == d_profid:
            p_name =  pitem['name']
            p_ver = pitem['customerVersion']

    if d_type == "ATS":
        d_ip = ditem['outputs'][0]['ipSettings']['ipAddress']
        d_udp = str(ditem['outputs'][0]['ipSettings']['ipPort'])
        d_clid = ditem['outputs'][0]['ipSettings']['cloudlinkGroupId']
        for citem in cl:
            c_id = citem['id']
            if c_id == d_clid:
                d_cl = citem['name']
                d_eclid = citem['id']
    else:
        d_ip = 'NA'
        d_udp = 'NA'
        d_cl = 'NA'
        d_eclid = 'NA'

    #print '*'.join((sv_name,sv_state,sr_name,sr_cl,sr_sip,sr_mip,sr_udp,d_name,d_type,d_ip,d_udp,d_cl,p_name,p_ver))
    print '*'.join((d_name,d_id,d_type,d_ip,d_udp,d_cl,d_eclid,p_name,d_profid,p_ver))
