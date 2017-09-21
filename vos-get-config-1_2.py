#!/usr/bin/env python

###########################################################
# Script: vos_get_config.py
# Author: John Vasconcelos
# Date: 04/18/2017
# Version 1.2
###########################################################

from pprint import pprint
import requests
import json
import vos

requests.packages.urllib3.disable_warnings()

api_proto = "https"

hostname = raw_input("Enter the VOS RT Address:\n")

api_get_serv = "/vos-api/configure/v1/services"

api_get_dest = "/vos-api/configure/v1/destinations"

api_get_src = "/vos-api/configure/v1/sources"

api_get_prof = "/vos-api/labwizard/v1/profiles"

api_get_cl = "/vos-api/uplink-hub/v1/uplinkGroups"

api_header_json = {'user-agent':'Accept:application/json'}

api_header_all = {'user-agent':'Accept: */*'}


vos_session = vos.vos_get_session()

vos_session.post(api_proto+'://'+hostname, verify=False)

vos_prof_req = vos_session.get(api_proto+'://'+hostname+api_get_prof,headers=api_header_all,verify=False)

vos_dest_req = vos_session.get(api_proto+'://'+hostname+api_get_dest,headers=api_header_json,verify=False)

vos_serv_req = vos_session.get(api_proto+'://'+hostname+api_get_serv,headers=api_header_all,verify=False)

vos_sour_req = vos_session.get(api_proto+'://'+hostname+api_get_src,headers=api_header_all,verify=False)

vos_cl_req = vos_session.get(api_proto+'://'+hostname+api_get_cl,headers=api_header_json,verify=False)

# Need to add a check here.
#if vos_dest_req.status_code !=200:
#    print vos_dest_req.status_code

d = vos_dest_req.json()

p = vos_prof_req.json()

sv = vos_serv_req.json()

sr = vos_sour_req.json()

cl = vos_cl_req.json()


print "*".join(("Service Name"  ,  "Service ID" , "State"  , "SRV Profile" , "SRV Prof Ver"  ,  "SRV Prof ID" , "Source Name" , "Source ID" ,  "SRC CL" , "SRC CL ID" , "SRC IP" ,\
                "SRC Mcast"   ,"SRC Port"  ,  "Destination Name" ,  "Dest ID" , "Dst Type" , "Publish Name",  "ATS Mcast" ,  "ATS Port"  ,  "ATS CL" , "ATC CL ID" ,  "Dest Profile"  ,  "Dest Prof Ver",\
                "Dest Prof ID"))


for svitem in sv:
    sv_id = svitem['id']
    sv_name =  svitem['name']
    sv_sour_id = svitem['serviceSources'][0]['sourceId']
    sv_dests_id = svitem['destinationsId']
    sv_prof_id = svitem['profileId']
    sv_state = svitem['controlState']

    
    for sv_dest_id in sv_dests_id:
        for pitem in p:
            p_id = pitem['id']
            if p_id == sv_prof_id:
                sr_p_name =  pitem['name']
                sr_p_ver = pitem['customerVersion']
    
        for ditem in d:
            d_id = ditem['id']
            if d_id == sv_dest_id:
                d_name = ditem['name']
                d_type = ditem['type']
                d_prof_id = ditem['destinationProfileId']
                if d_type == "ATS":
                    d_ip = ditem['outputs'][0]['ipSettings']['ipAddress']
                    d_udp = str(ditem['outputs'][0]['ipSettings']['ipPort'])
                    d_clid = ditem['outputs'][0]['ipSettings']['cloudlinkGroupId']
                    d_pub = 'NA'
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
                    for d_endpoint in ditem['outputs'][0]['originSettings']['originOutputEndPoints']:
                        if d_endpoint['publishName']:
                            d_pub = d_endpoint['publishName']
                for pitem in p:
                    p_id = pitem['id']
                    if p_id == d_prof_id:
                        d_p_name =  pitem['name']
                        d_p_ver = pitem['customerVersion']    
    
    
        for sritem in sr:
            sr_id = sritem['id']
            if sr_id == sv_sour_id:
                sr_name =  sritem['name']
                sr_clid = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['uplinkGroupId']
                sr_sip = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ssmIpAddresses'][0]
                sr_mip = sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ipAddress']
                sr_udp = str(sritem['inputs'][0]['zixiSettings']['harmonicUplinkSetting']['ipPort'])
                for citem in cl:
                    c_id = citem['id']
                    if c_id == sr_clid:
                        sr_cl = citem['name']
                        break
                    else:
                        sr_cl = "NA"

        #print '*'.join((sv_name,sv_state,sr_name,sr_cl,sr_sip,sr_mip,sr_udp,d_name,d_type,d_ip,d_udp,d_cl,p_name,p_ver))
        print '*'.join((sv_name,sv_id,sv_state,sr_p_name,sr_p_ver,sv_prof_id,sr_name,sv_sour_id,sr_cl,sr_clid,sr_sip,sr_mip,sr_udp,d_name,sv_dest_id,d_type,d_pub,d_ip,d_udp,d_cl,d_eclid,d_p_name,d_p_ver,d_prof_id))
